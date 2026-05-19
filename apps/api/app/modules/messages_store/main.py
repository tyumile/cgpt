from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message


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
    await session.commit()
    await session.refresh(message)
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
