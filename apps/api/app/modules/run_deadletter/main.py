from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentRun


async def mark_deadletter(session: AsyncSession, *, run: AgentRun, reason: str) -> AgentRun:
    run.deadletter_reason = reason
    await session.commit()
    await session.refresh(run)
    return run
