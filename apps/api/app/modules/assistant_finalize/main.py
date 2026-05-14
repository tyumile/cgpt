from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentRun
from app.modules.agent_runs.main import mark_run_done, mark_run_failed
from app.modules.messages_store.main import create_message, update_message


async def finalize_success(
    session: AsyncSession,
    *,
    run: AgentRun,
    workspace_id: int,
    chat_id: int,
    content: str,
) -> int:
    message = await create_message(
        session,
        workspace_id=workspace_id,
        chat_id=chat_id,
        role="assistant",
        content=content,
        status="streaming",
    )
    await update_message(session, message, status="done")
    await mark_run_done(session, run, output_message_id=message.id)
    return message.id


async def finalize_failure(session: AsyncSession, *, run: AgentRun, error: str) -> None:
    await mark_run_failed(session, run, error=error)
