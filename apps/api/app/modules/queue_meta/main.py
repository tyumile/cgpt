from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentRun


async def set_enqueued(session: AsyncSession, run: AgentRun, *, job_id: str) -> AgentRun:
    run.queue_job_id = job_id
    run.status = "queued"
    run.error = None
    await session.commit()
    await session.refresh(run)
    return run
