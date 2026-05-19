from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message, UploadedFile


async def create_message(
    session: AsyncSession,
    *,
    workspace_id: int,
    chat_id: int,
    role: str,
    content: str,
    status: str,
) -> Message:
    message = Message(
        workspace_id=workspace_id,
        chat_id=chat_id,
        role=role,
        content=content,
        status=status,
    )
    session.add(message)
    await session.execute(
        text("UPDATE chats SET updated_at = now() WHERE id = :chat_id"),
        {"chat_id": chat_id},
    )
    await session.flush()
    return message


async def update_message(
    session: AsyncSession,
    message: Message,
    *,
    content: str | None = None,
    status: str | None = None,
) -> Message:
    if content is not None:
        message.content = content
    if status is not None:
        message.status = status
    await session.commit()
    await session.refresh(message)
    return message


async def get_chat_messages(session: AsyncSession, *, chat_id: int) -> list[Message]:
    result = await session.execute(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.asc()))
    return list(result.scalars().all())


async def get_last_messages(session: AsyncSession, *, chat_id: int, limit: int) -> list[Message]:
    result = await session.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(desc(Message.created_at)).limit(limit)
    )
    rows = list(result.scalars().all())
    rows.reverse()
    return rows


async def create_uploaded_file(
    session: AsyncSession,
    *,
    user_id: int,
    chat_id: int,
    message_id: int,
    original_name: str,
    stored_name: str,
    relative_path: str,
    mime_type: str,
    size_bytes: int,
) -> UploadedFile:
    row = UploadedFile(
        user_id=user_id,
        chat_id=chat_id,
        message_id=message_id,
        original_name=original_name,
        stored_name=stored_name,
        relative_path=relative_path,
        mime_type=mime_type,
        size_bytes=size_bytes,
        preview_text=None,
    )
    session.add(row)
    await session.flush()
    return row


async def list_uploaded_files_by_message_ids(
    session: AsyncSession, *, message_ids: list[int]
) -> dict[int, list[UploadedFile]]:
    if not message_ids:
        return {}
    result = await session.execute(
        select(UploadedFile)
        .where(UploadedFile.message_id.in_(message_ids))
        .order_by(UploadedFile.created_at.asc(), UploadedFile.id.asc())
    )
    rows = list(result.scalars().all())
    grouped: dict[int, list[UploadedFile]] = {}
    for row in rows:
        if row.message_id is None:
            continue
        grouped.setdefault(row.message_id, []).append(row)
    return grouped


async def list_uploaded_files_for_message(
    session: AsyncSession, *, message_id: int
) -> list[UploadedFile]:
    result = await session.execute(
        select(UploadedFile)
        .where(UploadedFile.message_id == message_id)
        .order_by(UploadedFile.created_at.asc(), UploadedFile.id.asc())
    )
    return list(result.scalars().all())


async def get_uploaded_file_for_chat(
    session: AsyncSession, *, chat_id: int, user_id: int, file_id: int
) -> UploadedFile | None:
    result = await session.execute(
        select(UploadedFile).where(
            UploadedFile.id == file_id,
            UploadedFile.chat_id == chat_id,
            UploadedFile.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()
