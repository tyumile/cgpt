import json
import uuid
from dataclasses import asdict, dataclass

from redis.asyncio import Redis

from app.config.main import get_settings


@dataclass(slots=True)
class RunJob:
    job_id: str
    run_id: int
    workspace_id: int
    chat_id: int
    trigger_message_id: int


def build_job(*, run_id: int, workspace_id: int, chat_id: int, trigger_message_id: int) -> RunJob:
    return RunJob(
        job_id=str(uuid.uuid4()),
        run_id=run_id,
        workspace_id=workspace_id,
        chat_id=chat_id,
        trigger_message_id=trigger_message_id,
    )


async def enqueue_run(redis: Redis, job: RunJob) -> str:
    settings = get_settings()
    payload = json.dumps(asdict(job), ensure_ascii=False)
    await redis.lpush(settings.run_queue_name, payload)
    return job.job_id
