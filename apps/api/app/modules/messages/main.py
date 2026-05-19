import logging
import re
import unicodedata
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.db.models import Chat, Message, UploadedFile
from app.modules.agent_runs.main import create_agent_run, mark_run_failed
from app.modules.cabinet_session.main import resolve_cabinet_session_from_request
from app.modules.messages_store.main import (
    create_message,
    create_uploaded_file,
    get_chat_messages,
    get_uploaded_file_for_chat,
    list_uploaded_files_by_message_ids,
)
from app.modules.queue_meta.main import set_enqueued
from app.modules.run_enqueuer.main import build_job, enqueue_run
from app.modules.realtime.main import publish_event
from app.modules.workspaces.main import get_current_workspace
from app.shared.redis_client import get_redis
from app.shared.schemas import MessagePostResponse, MessageResponse, UploadedFileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chats/{chat_id}/messages", tags=["messages"])

DEFAULT_CHAT_TITLE = "Новый чат"
CHAT_TITLE_MAX_LEN = 255
MAX_FILES_PER_MESSAGE = 10
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
UPLOAD_DIR_NAME = "uploads"
_BLOCKED_EXTENSIONS = {
    ".exe",
    ".dll",
    ".bat",
    ".cmd",
    ".com",
    ".msi",
    ".ps1",
    ".vbs",
    ".js",
    ".jse",
    ".jar",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".py",
    ".php",
    ".pl",
    ".rb",
    ".apk",
    ".app",
    ".dmg",
}
_BLOCKED_MIME_TYPES = {
    "application/x-msdownload",
    "application/x-dosexec",
    "application/x-sh",
    "application/x-bat",
    "application/x-csh",
    "application/x-executable",
    "application/javascript",
    "text/javascript",
    "text/x-shellscript",
    "text/x-python",
    "text/x-php",
}
_LEADING_NOISE_RE = re.compile(
    r"^(?:user|assistant|system|bot|пользователь|ассистент|система|вопрос|question|запрос|request)\s*[:>\-\]]\s*",
    re.IGNORECASE,
)
_LEADING_PUNCT_RE = re.compile(r"^[\s\-*#>.,:;!?()\[\]\"'`]+")


async def _get_owned_chat_or_404(session: AsyncSession, *, chat_id: int, user_id: int, workspace_id: int) -> Chat:
    result = await session.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id, Chat.workspace_id == workspace_id)
    )
    chat = result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


def _build_chat_title_from_first_message(content: str) -> str:
    cleaned = re.sub(r"\s+", " ", content.strip())
    cleaned = _LEADING_NOISE_RE.sub("", cleaned)
    cleaned = _LEADING_PUNCT_RE.sub("", cleaned).strip()
    if not cleaned:
        return DEFAULT_CHAT_TITLE
    return cleaned[:CHAT_TITLE_MAX_LEN]


async def _maybe_set_initial_chat_title(
    session: AsyncSession, *, chat: Chat, user_message: Message, message_content: str
) -> None:
    if chat.title != DEFAULT_CHAT_TITLE:
        return

    first_user_message_result = await session.execute(
        select(Message.id)
        .where(Message.chat_id == chat.id, Message.role == "user")
        .order_by(Message.created_at.asc(), Message.id.asc())
        .limit(1)
    )
    first_user_message_id = first_user_message_result.scalar_one_or_none()
    if first_user_message_id != user_message.id:
        return

    chat.title = _build_chat_title_from_first_message(message_content)


def _normalize_filename(raw_name: str) -> str:
    base = Path(raw_name).name
    normalized = unicodedata.normalize("NFKC", base)
    safe = "".join(ch for ch in normalized if ch.isprintable())
    safe = safe.replace("/", "_").replace("\\", "_").strip()
    if not safe:
        safe = "file"
    if len(safe) > 200:
        stem = Path(safe).stem[:150]
        suffix = Path(safe).suffix[:40]
        safe = f"{stem}{suffix}" if suffix else stem
    return safe


def _validate_file_type(*, filename: str, mime_type: str) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix and suffix in _BLOCKED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type is blocked: {suffix}")
    if mime_type.lower() in _BLOCKED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"MIME type is blocked: {mime_type}")


def _resolve_upload_dir(*, workspace_root: str, user_id: int, chat_id: int) -> Path:
    workspace = Path(workspace_root).resolve()
    directory = workspace / UPLOAD_DIR_NAME / f"user_{user_id}" / f"chat_{chat_id}"
    directory.mkdir(parents=True, exist_ok=True)
    resolved = directory.resolve()
    if not resolved.is_relative_to(workspace):
        raise HTTPException(status_code=400, detail="Resolved upload path is outside workspace")
    return resolved


def _build_download_path(*, chat_id: int, file_id: int) -> str:
    return f"/api/chats/{chat_id}/messages/files/{file_id}"


def _to_uploaded_file_response(row: UploadedFile) -> UploadedFileResponse:
    return UploadedFileResponse(
        id=row.id,
        original_name=row.original_name,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        created_at=row.created_at,
        download_path=_build_download_path(chat_id=row.chat_id, file_id=row.id),
    )


def _to_message_response(message: Message, attachments: list[UploadedFile]) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        workspace_id=message.workspace_id,
        chat_id=message.chat_id,
        role=message.role,
        content=message.content,
        status=message.status,
        created_at=message.created_at,
        updated_at=message.updated_at,
        attachments=[_to_uploaded_file_response(row) for row in attachments],
    )


async def _write_upload_file(upload: UploadFile, destination: Path) -> int:
    total_size = 0
    try:
        with destination.open("wb") as handle:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(status_code=413, detail="File is too large. Maximum is 20MB per file.")
                handle.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()
    return total_size


async def _cleanup_saved_paths(paths: list[Path]) -> None:
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except Exception:  # pragma: no cover
            logger.warning("Failed to cleanup uploaded file", extra={"path": str(path)})


@router.get("", response_model=list[MessageResponse])
async def list_messages(
    chat_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> list[MessageResponse]:
    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    await _get_owned_chat_or_404(
        session,
        chat_id=chat_id,
        user_id=cabinet_session.user_id,
        workspace_id=workspace.id,
    )

    messages = await get_chat_messages(session, chat_id=chat_id)
    message_ids = [message.id for message in messages]
    attachments_by_message_id = await list_uploaded_files_by_message_ids(session, message_ids=message_ids)

    return [_to_message_response(message, attachments_by_message_id.get(message.id, [])) for message in messages]


@router.get("/files/{file_id}")
async def download_uploaded_file(
    chat_id: int,
    file_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    await _get_owned_chat_or_404(
        session,
        chat_id=chat_id,
        user_id=cabinet_session.user_id,
        workspace_id=workspace.id,
    )

    upload = await get_uploaded_file_for_chat(
        session,
        chat_id=chat_id,
        user_id=cabinet_session.user_id,
        file_id=file_id,
    )
    if upload is None:
        raise HTTPException(status_code=404, detail="File not found")

    workspace_path = Path(workspace.root_path).resolve()
    file_path = (workspace_path / upload.relative_path).resolve()
    if not file_path.is_relative_to(workspace_path):
        raise HTTPException(status_code=400, detail="File path is invalid")
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File is missing on disk")

    return FileResponse(
        path=str(file_path),
        media_type=upload.mime_type,
        filename=upload.original_name,
    )


@router.post("", response_model=MessagePostResponse)
async def create_user_message(
    chat_id: int,
    request: Request,
    content: Annotated[str, Form(...)],
    files: Annotated[list[UploadFile] | None, File()] = None,
    session: AsyncSession = Depends(get_session),
) -> MessagePostResponse:
    if not request.headers.get("content-type", "").lower().startswith("multipart/form-data"):
        raise HTTPException(status_code=415, detail="Use multipart/form-data for message creation")

    cleaned_content = content.strip()
    if not cleaned_content:
        raise HTTPException(status_code=400, detail="Message content is required")
    validation_probe = re.sub(r"\s+", " ", cleaned_content)
    validation_probe = _LEADING_NOISE_RE.sub("", validation_probe)
    validation_probe = _LEADING_PUNCT_RE.sub("", validation_probe).strip()
    if not validation_probe:
        raise HTTPException(status_code=400, detail="Message content is required")

    files = files or []

    if len(files) > MAX_FILES_PER_MESSAGE:
        raise HTTPException(status_code=400, detail="Too many files. Maximum is 10 files per message.")

    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    chat = await _get_owned_chat_or_404(
        session,
        chat_id=chat_id,
        user_id=cabinet_session.user_id,
        workspace_id=workspace.id,
    )

    workspace_path = Path(workspace.root_path).resolve()
    upload_dir = _resolve_upload_dir(workspace_root=workspace.root_path, user_id=cabinet_session.user_id, chat_id=chat_id)

    persisted_paths: list[Path] = []
    persisted_file_payloads: list[dict[str, object]] = []

    try:
        for upload in files:
            if not upload.filename:
                raise HTTPException(status_code=400, detail="Uploaded file must have a file name")
            safe_name = _normalize_filename(upload.filename)
            mime_type = (upload.content_type or "application/octet-stream").lower()
            _validate_file_type(filename=safe_name, mime_type=mime_type)

            stored_name = f"{uuid.uuid4().hex}_{safe_name}"
            target_path = (upload_dir / stored_name).resolve()
            if not target_path.is_relative_to(workspace_path):
                raise HTTPException(status_code=400, detail="Target file path is invalid")

            size_bytes = await _write_upload_file(upload, target_path)
            relative_path = target_path.relative_to(workspace_path).as_posix()
            persisted_paths.append(target_path)
            persisted_file_payloads.append(
                {
                    "original_name": safe_name,
                    "stored_name": stored_name,
                    "relative_path": relative_path,
                    "mime_type": mime_type,
                    "size_bytes": size_bytes,
                }
            )
    except HTTPException:
        await _cleanup_saved_paths(persisted_paths)
        raise
    except Exception as exc:  # pragma: no cover
        await _cleanup_saved_paths(persisted_paths)
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded files: {exc}") from exc

    logger.info("Incoming user message", extra={"chat_id": chat_id, "file_count": len(persisted_file_payloads)})
    try:
        user_message = await create_message(
            session,
            workspace_id=chat.workspace_id,
            chat_id=chat_id,
            role="user",
            content=cleaned_content,
            status="done",
        )
        await _maybe_set_initial_chat_title(session, chat=chat, user_message=user_message, message_content=cleaned_content)

        for file_payload in persisted_file_payloads:
            await create_uploaded_file(
                session,
                user_id=cabinet_session.user_id,
                chat_id=chat_id,
                message_id=user_message.id,
                original_name=str(file_payload["original_name"]),
                stored_name=str(file_payload["stored_name"]),
                relative_path=str(file_payload["relative_path"]),
                mime_type=str(file_payload["mime_type"]),
                size_bytes=int(file_payload["size_bytes"]),
            )

        run = await create_agent_run(
            session,
            workspace_id=chat.workspace_id,
            chat_id=chat_id,
            trigger_message_id=user_message.id,
        )
        await session.commit()
    except HTTPException:
        await session.rollback()
        await _cleanup_saved_paths(persisted_paths)
        raise
    except Exception as exc:
        await session.rollback()
        await _cleanup_saved_paths(persisted_paths)
        raise HTTPException(status_code=500, detail=f"Failed to persist message and attachment data: {exc}") from exc

    redis = get_redis()
    job = build_job(
        run_id=run.id,
        workspace_id=chat.workspace_id,
        chat_id=chat_id,
        trigger_message_id=user_message.id,
    )

    try:
        await set_enqueued(session, run, job_id=job.job_id)
        await enqueue_run(redis, job)
    except RedisError as exc:
        error = "Queue is temporarily unavailable. Please retry."
        await mark_run_failed(session, run, error=error)
        await publish_event(
            chat_id,
            {
                "event": "assistant_error",
                "agent_run_id": run.id,
                "error": error,
            },
        )
        raise HTTPException(status_code=503, detail=error) from exc

    logger.info("Agent run queued", extra={"chat_id": chat_id, "run_id": run.id, "job_id": job.job_id})
    return MessagePostResponse(message_id=user_message.id, agent_run_id=run.id)
