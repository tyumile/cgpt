from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.db.models import Chat, Message
from app.modules.cabinet_session.main import resolve_cabinet_session_from_request
from app.modules.workspaces.main import get_current_workspace
from app.shared.schemas import ChatCreateRequest, ChatResponse

router = APIRouter(prefix="/api/chats", tags=["chats"])


def _chat_response(chat: Chat, preview_first_message: str | None) -> ChatResponse:
    payload = ChatResponse.model_validate(chat, from_attributes=True).model_dump()
    payload["preview_first_message"] = preview_first_message
    return ChatResponse(**payload)


@router.post("", response_model=ChatResponse)
async def create_chat(
    payload: ChatCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    workspace = await get_current_workspace(session)
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    chat = Chat(workspace_id=workspace.id, user_id=cabinet_session.user_id, title=payload.title or "New chat")
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
            Chat.id == chat_id, Chat.user_id == cabinet_session.user_id
        )
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return _chat_response(chat=row[0], preview_first_message=row[1])
