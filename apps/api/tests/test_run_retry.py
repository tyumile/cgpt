from app.modules.run_retry.main import is_transient_error, should_retry


def test_transient_classifier() -> None:
    assert is_transient_error("connection timeout")
    assert not is_transient_error("invalid input format")


def test_should_retry_budget() -> None:
    assert should_retry(attempt=1, max_retries=1, error="network timeout")
    assert not should_retry(attempt=2, max_retries=1, error="network timeout")
    assert not should_retry(attempt=1, max_retries=1, error="bad request")
