from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentRun


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def create_agent_run(
    session: AsyncSession,
    *,
    workspace_id: int,
    chat_id: int,
    trigger_message_id: int,
) -> AgentRun:
    run = AgentRun(
        workspace_id=workspace_id,
        chat_id=chat_id,
        trigger_message_id=trigger_message_id,
        status="queued",
        attempt=0,
    )
    session.add(run)
    await session.flush()
    return run


async def claim_run_for_processing(
    session: AsyncSession,
    *,
    run_id: int,
    job_id: str,
    lease_seconds: int,
) -> AgentRun | None:
    result = await session.execute(select(AgentRun).where(AgentRun.id == run_id).with_for_update(skip_locked=True))
    run = result.scalar_one_or_none()
    if run is None:
        return None

    now = _now()
    if run.queue_job_id is not None and run.queue_job_id != job_id:
        return None
    can_claim = run.status == "queued" or (run.status == "running" and run.lease_expires_at and run.lease_expires_at < now)
    if not can_claim:
        return None

    run.status = "running"
    run.started_at = run.started_at or now
    run.attempt = (run.attempt or 0) + 1
    run.heartbeat_at = now
    run.lease_expires_at = now + timedelta(seconds=lease_seconds)
    await session.commit()
    await session.refresh(run)
    return run


async def mark_run_running(session: AsyncSession, run: AgentRun) -> AgentRun:
    run.status = "running"
    run.started_at = run.started_at or _now()
    await session.commit()
    await session.refresh(run)
    return run


async def heartbeat_run(session: AsyncSession, run: AgentRun, *, lease_seconds: int) -> AgentRun:
    now = _now()
    run.heartbeat_at = now
    run.lease_expires_at = now + timedelta(seconds=lease_seconds)
    await session.commit()
    await session.refresh(run)
    return run


async def mark_run_done(session: AsyncSession, run: AgentRun, *, output_message_id: int) -> AgentRun:
    run.status = "done"
    run.output_message_id = output_message_id
    run.finished_at = _now()
    run.error = None
    run.lease_expires_at = None
    run.heartbeat_at = None
    await session.commit()
    await session.refresh(run)
    return run


async def mark_run_failed(session: AsyncSession, run: AgentRun, *, error: str) -> AgentRun:
    run.status = "failed"
    run.finished_at = _now()
    run.error = error
    run.lease_expires_at = None
    run.heartbeat_at = None
    await session.commit()
    await session.refresh(run)
    return run


async def reset_run_to_queued(session: AsyncSession, run: AgentRun, *, error: str | None = None) -> AgentRun:
    run.status = "queued"
    run.error = error
    run.lease_expires_at = None
    run.heartbeat_at = None
    await session.commit()
    await session.refresh(run)
    return run


async def list_stale_running_runs(session: AsyncSession, *, limit: int = 100) -> list[AgentRun]:
    now = _now()
    result = await session.execute(
        select(AgentRun)
        .where(AgentRun.status == "running")
        .where(AgentRun.lease_expires_at.is_not(None))
        .where(AgentRun.lease_expires_at < now)
        .limit(limit)
    )
    return list(result.scalars().all())
