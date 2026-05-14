TRANSIENT_MARKERS = (
    "timeout",
    "temporarily unavailable",
    "connection reset",
    "connection refused",
    "network",
)


def is_transient_error(error: str) -> bool:
    lowered = error.lower()
    return any(marker in lowered for marker in TRANSIENT_MARKERS)


def should_retry(*, attempt: int, max_retries: int, error: str) -> bool:
    return attempt <= max_retries and is_transient_error(error)
