import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.db.models import Chat
from app.modules.agent_runs.main import create_agent_run, mark_run_failed
from app.modules.cabinet_session.main import resolve_cabinet_session_from_request
from app.modules.messages_store.main import create_message, get_chat_messages
from app.modules.queue_meta.main import set_enqueued
from app.modules.run_enqueuer.main import build_job, enqueue_run
from app.modules.realtime.main import publish_event
from app.shared.redis_client import get_redis
from app.shared.schemas import MessageCreateRequest, MessagePostResponse, MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chats/{chat_id}/messages", tags=["messages"])


async def _get_owned_chat_or_404(session: AsyncSession, *, chat_id: int, user_id: int) -> Chat:
    result = await session.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id))
    chat = result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.get("", response_model=list[MessageResponse])
async def list_messages(
    chat_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> list[MessageResponse]:
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    await _get_owned_chat_or_404(session, chat_id=chat_id, user_id=cabinet_session.user_id)

    messages = await get_chat_messages(session, chat_id=chat_id)
    return [MessageResponse.model_validate(message, from_attributes=True) for message in messages]


@router.post("", response_model=MessagePostResponse)
async def create_user_message(
    chat_id: int,
    payload: MessageCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> MessagePostResponse:
    cabinet_session = await resolve_cabinet_session_from_request(request, session)
    chat = await _get_owned_chat_or_404(session, chat_id=chat_id, user_id=cabinet_session.user_id)

    logger.info("Incoming user message", extra={"chat_id": chat_id})

    user_message = await create_message(
        session,
        workspace_id=chat.workspace_id,
        chat_id=chat_id,
        role="user",
        content=payload.content,
        status="done",
    )

    run = await create_agent_run(
        session,
        workspace_id=chat.workspace_id,
        chat_id=chat_id,
        trigger_message_id=user_message.id,
    )

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
