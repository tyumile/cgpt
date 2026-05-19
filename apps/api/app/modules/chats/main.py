from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.db.models import AgentRun, Chat, Message
from app.modules.cabinet_session.main import resolve_cabinet_session_from_request
from app.modules.workspaces.main import get_current_workspace
from app.shared.schemas import ChatCreateRequest, ChatResponse

router = APIRouter(prefix="/api/chats", tags=["chats"])
DEFAULT_CHAT_TITLE = "Новый чат"


def _chat_response(chat: Chat, preview_first_message: str | None) -> ChatResponse:
    payload = ChatResponse.model_validate(chat, from_attributes=True).model_dump()
    payload["preview_first_message"] = preview_first_message
    return ChatResponse(**payload)


async def _delete_chat_transactional(chat_id: int, request: Request, session: AsyncSession) -> None:
    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    chat_result = await session.execute(
        select(Chat)
        .where(
            Chat.id == chat_id,
            Chat.user_id == cabinet_session.user_id,
            Chat.workspace_id == workspace.id,
        )
        .with_for_update()
    )
    chat = chat_result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    now = datetime.now(timezone.utc)
    await session.execute(
        update(AgentRun)
        .where(AgentRun.chat_id == chat_id, AgentRun.status.in_(("queued", "running")))
        .values(
            status="failed",
            error="Chat deleted by user",
            finished_at=now,
            lease_expires_at=None,
            heartbeat_at=None,
        )
    )

    workspace_root = Path(workspace.root_path).resolve()
    uploaded_files = (
        await session.execute(
            text("SELECT relative_path FROM uploaded_files WHERE chat_id = :chat_id"),
            {"chat_id": chat_id},
        )
    ).mappings().all()
    for row in uploaded_files:
        relative_path = str(row["relative_path"])
        file_path = (workspace_root / relative_path).resolve()
        if file_path.is_relative_to(workspace_root):
            file_path.unlink(missing_ok=True)

    await session.execute(text("DELETE FROM uploaded_files WHERE chat_id = :chat_id"), {"chat_id": chat_id})
    await session.execute(delete(AgentRun).where(AgentRun.chat_id == chat_id))
    await session.execute(delete(Message).where(Message.chat_id == chat_id))
    await session.execute(delete(Chat).where(Chat.id == chat_id))


@router.post("", response_model=ChatResponse)
async def create_chat(
    payload: ChatCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    chat = Chat(workspace_id=workspace.id, user_id=cabinet_session.user_id, title=payload.title or DEFAULT_CHAT_TITLE)
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return _chat_response(chat, preview_first_message=None)


@router.get("", response_model=list[ChatResponse])
async def list_chats(request: Request, session: AsyncSession = Depends(get_session)) -> list[ChatResponse]:
    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    first_message_subquery = (
        select(Message.content)
        .where(Message.chat_id == Chat.id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .limit(1)
        .scalar_subquery()
    )
    result = await session.execute(
        select(Chat, first_message_subquery.label("preview_first_message"))
        .where(Chat.workspace_id == workspace.id, Chat.user_id == cabinet_session.user_id)
        .order_by(Chat.updated_at.desc(), Chat.id.desc())
    )
    rows = result.all()
    return [_chat_response(chat=row[0], preview_first_message=row[1]) for row in rows]


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> ChatResponse:
    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    first_message_subquery = (
        select(Message.content)
        .where(Message.chat_id == Chat.id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .limit(1)
        .scalar_subquery()
    )
    result = await session.execute(
        select(Chat, first_message_subquery.label("preview_first_message")).where(
            Chat.id == chat_id,
            Chat.user_id == cabinet_session.user_id,
            Chat.workspace_id == workspace.id,
        )
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return _chat_response(chat=row[0], preview_first_message=row[1])


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: int, request: Request, session: AsyncSession = Depends(get_session)) -> Response:
    in_transaction = getattr(session, "in_transaction", None)
    if callable(in_transaction) and in_transaction():
        await _delete_chat_transactional(chat_id, request, session)
    else:
        async with session.begin():
            await _delete_chat_transactional(chat_id, request, session)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
