import asyncio
from types import SimpleNamespace

from app.modules.agent_runs.main import claim_run_for_processing


class _FakeResult:
    def __init__(self, run):
        self._run = run

    def scalar_one_or_none(self):
        return self._run


class _FakeSession:
    def __init__(self, run):
        self.run = run
        self.statement = None
        self.commit_calls = 0
        self.refresh_calls = 0

    async def execute(self, statement):
        self.statement = statement
        return _FakeResult(self.run)

    async def commit(self):
        self.commit_calls += 1

    async def refresh(self, _run):
        self.refresh_calls += 1


def test_claim_run_uses_row_lock_and_updates_lease() -> None:
    run = SimpleNamespace(
        status="queued",
        queue_job_id="job-1",
        started_at=None,
        attempt=0,
        heartbeat_at=None,
        lease_expires_at=None,
    )
    session = _FakeSession(run)

    claimed = asyncio.run(
        claim_run_for_processing(
            session,
            run_id=7,
            job_id="job-1",
            lease_seconds=30,
        )
    )

    assert claimed is run
    assert session.statement._for_update_arg is not None
    assert run.status == "running"
    assert run.attempt == 1
    assert run.started_at is not None
    assert run.heartbeat_at is not None
    assert run.lease_expires_at is not None
    assert run.lease_expires_at > run.heartbeat_at
    assert session.commit_calls == 1
    assert session.refresh_calls == 1


def test_claim_run_rejects_job_id_mismatch() -> None:
    run = SimpleNamespace(
        status="queued",
        queue_job_id="job-expected",
        started_at=None,
        attempt=0,
        heartbeat_at=None,
        lease_expires_at=None,
    )
    session = _FakeSession(run)

    claimed = asyncio.run(
        claim_run_for_processing(
            session,
            run_id=8,
            job_id="job-other",
            lease_seconds=30,
        )
    )

    assert claimed is None
    assert session.statement._for_update_arg is not None
    assert session.commit_calls == 0
    assert run.status == "queued"
