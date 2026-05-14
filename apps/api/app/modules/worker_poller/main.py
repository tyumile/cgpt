import asyncio
import json
import logging
from dataclasses import dataclass

from sqlalchemy import select

from app.config.main import get_settings
from app.db.main import AsyncSessionLocal
from app.db.models import AgentRun
from app.modules.agent_exec.main import process_agent_run
from app.modules.agent_runs.main import claim_run_for_processing, list_stale_running_runs, mark_run_failed, reset_run_to_queued
from app.modules.run_deadletter.main import mark_deadletter
from app.modules.run_enqueuer.main import build_job
from app.modules.run_retry.main import should_retry
from app.shared.redis_client import get_redis

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class QueuePayload:
    job_id: str
    run_id: int
    workspace_id: int
    chat_id: int
    trigger_message_id: int

    @classmethod
    def from_json(cls, value: str) -> "QueuePayload":
        data = json.loads(value)
        return cls(**data)


async def _ack_processing_message(raw_payload: str) -> None:
    settings = get_settings()
    redis = get_redis()
    await redis.lrem(settings.run_processing_queue_name, 1, raw_payload)


async def _requeue_payload(payload: QueuePayload) -> None:
    settings = get_settings()
    redis = get_redis()
    await redis.lpush(settings.run_queue_name, json.dumps(payload.__dict__, ensure_ascii=False))


async def _run_reaper_once() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        stale = await list_stale_running_runs(session)
        if not stale:
            return
        for run in stale:
            if run.attempt <= settings.run_max_retries:
                await reset_run_to_queued(session, run, error="Lease expired, re-queued")
                payload = build_job(
                    run_id=run.id,
                    workspace_id=run.workspace_id,
                    chat_id=run.chat_id,
                    trigger_message_id=run.trigger_message_id,
                )
                payload.job_id = run.queue_job_id or payload.job_id
                await _requeue_payload(QueuePayload(**payload.__dict__))
            else:
                await mark_run_failed(session, run, error="Lease expired and retry budget exhausted")
                await mark_deadletter(session, run=run, reason="stale-running")


async def worker_loop() -> None:
    settings = get_settings()
    redis = get_redis()
    last_reaper = 0.0

    while True:
        now = asyncio.get_event_loop().time()
        if now - last_reaper >= settings.run_reaper_interval_seconds:
            await _run_reaper_once()
            last_reaper = now

        raw_payload = await redis.execute_command(
            "BLMOVE",
            settings.run_queue_name,
            settings.run_processing_queue_name,
            "RIGHT",
            "LEFT",
            settings.run_queue_block_seconds,
        )

        if raw_payload is None:
            await asyncio.sleep(0.1)
            continue

        payload = QueuePayload.from_json(raw_payload)

        async with AsyncSessionLocal() as session:
            run = await claim_run_for_processing(session, run_id=payload.run_id, lease_seconds=settings.run_lease_seconds)
            if run is None:
                await _ack_processing_message(raw_payload)
                continue

        try:
            await process_agent_run(run_id=payload.run_id, chat_id=payload.chat_id)
            await _ack_processing_message(raw_payload)
        except Exception as exc:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(AgentRun).where(AgentRun.id == payload.run_id))
                run = result.scalar_one_or_none()
                if run is None:
                    await _ack_processing_message(raw_payload)
                    continue

                error = str(exc)
                if should_retry(attempt=run.attempt, max_retries=settings.run_max_retries, error=error):
                    await reset_run_to_queued(session, run, error=error)
                    await _requeue_payload(payload)
                    await _ack_processing_message(raw_payload)
                else:
                    await mark_deadletter(session, run=run, reason=error)
                    await _ack_processing_message(raw_payload)
