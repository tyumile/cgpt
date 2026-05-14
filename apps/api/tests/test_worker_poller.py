import asyncio

from app.modules.worker_poller.main import QueuePayload, _recover_processing_queue_once


class _FakeRedis:
    def __init__(self, *, processing, queue=None):
        self.processing = list(processing)
        self.queue = list(queue or [])

    async def lrange(self, name, start, end):
        assert name == "agent_runs:processing"
        assert start == 0
        assert end == -1
        return list(self.processing)

    async def lrem(self, name, count, value):
        assert name == "agent_runs:processing"
        assert count == 0
        self.processing = [item for item in self.processing if item != value]

    async def lpush(self, name, value):
        assert name == "agent_runs:queue"
        self.queue.insert(0, value)


class _FakeResult:
    def __init__(self, run):
        self._run = run

    def scalar_one_or_none(self):
        return self._run


class _FakeSession:
    def __init__(self, runs):
        self._runs = runs

    async def execute(self, statement):
        run_id = next(iter(statement.compile().params.values()))
        return _FakeResult(self._runs.get(run_id))


class _FakeSessionFactory:
    def __init__(self, runs):
        self._runs = runs

    def __call__(self):
        return self

    async def __aenter__(self):
        return _FakeSession(self._runs)

    async def __aexit__(self, exc_type, exc, tb):
        return False


def test_recover_processing_queue_requeues_only_safe_payloads() -> None:
    queued = QueuePayload(job_id="job-1", run_id=1, workspace_id=1, chat_id=1, trigger_message_id=11)
    done = QueuePayload(job_id="job-2", run_id=2, workspace_id=1, chat_id=1, trigger_message_id=12)
    failed = QueuePayload(job_id="job-3", run_id=3, workspace_id=1, chat_id=1, trigger_message_id=13)
    running = QueuePayload(job_id="job-4", run_id=4, workspace_id=1, chat_id=1, trigger_message_id=14)
    missing = QueuePayload(job_id="job-5", run_id=5, workspace_id=1, chat_id=1, trigger_message_id=15)

    queued_raw = '{"job_id": "job-1", "run_id": 1, "workspace_id": 1, "chat_id": 1, "trigger_message_id": 11}'
    done_raw = '{"job_id": "job-2", "run_id": 2, "workspace_id": 1, "chat_id": 1, "trigger_message_id": 12}'
    failed_raw = '{"job_id": "job-3", "run_id": 3, "workspace_id": 1, "chat_id": 1, "trigger_message_id": 13}'
    running_raw = '{"job_id": "job-4", "run_id": 4, "workspace_id": 1, "chat_id": 1, "trigger_message_id": 14}'
    missing_raw = '{"job_id": "job-5", "run_id": 5, "workspace_id": 1, "chat_id": 1, "trigger_message_id": 15}'

    redis = _FakeRedis(
        processing=[queued_raw, queued_raw, done_raw, failed_raw, running_raw, missing_raw],
    )
    session_factory = _FakeSessionFactory(
        {
            1: type("Run", (), {"status": "queued"})(),
            2: type("Run", (), {"status": "done"})(),
            3: type("Run", (), {"status": "failed"})(),
            4: type("Run", (), {"status": "running"})(),
        }
    )

    asyncio.run(_recover_processing_queue_once(redis=redis, session_factory=session_factory))

    assert redis.queue == [queued_raw]
    assert redis.processing == [running_raw]
