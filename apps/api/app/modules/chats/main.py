from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.db.models import Chat
from app.modules.workspaces.main import get_current_workspace
from app.shared.schemas import ChatCreateRequest, ChatResponse

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.post("", response_model=ChatResponse)
async def create_chat(payload: ChatCreateRequest, session: AsyncSession = Depends(get_session)) -> ChatResponse:
    workspace = await get_current_workspace(session)
    chat = Chat(workspace_id=workspace.id, title=payload.title or "New chat")
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return ChatResponse.model_validate(chat, from_attributes=True)


@router.get("", response_model=list[ChatResponse])
async def list_chats(session: AsyncSession = Depends(get_session)) -> list[ChatResponse]:
    workspace = await get_current_workspace(session)
    result = await session.execute(
        select(Chat).where(Chat.workspace_id == workspace.id).order_by(Chat.updated_at.desc(), Chat.id.desc())
    )
    chats = list(result.scalars().all())
    return [ChatResponse.model_validate(chat, from_attributes=True) for chat in chats]


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: int, session: AsyncSession = Depends(get_session)) -> ChatResponse:
    result = await session.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatResponse.model_validate(chat, from_attributes=True)
