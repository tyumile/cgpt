from app.modules.run_enqueuer.main import build_job


def test_build_job_payload() -> None:
    job = build_job(run_id=5, workspace_id=1, chat_id=7, trigger_message_id=9)
    assert job.run_id == 5
    assert job.workspace_id == 1
    assert job.chat_id == 7
    assert job.trigger_message_id == 9
    assert job.job_id
