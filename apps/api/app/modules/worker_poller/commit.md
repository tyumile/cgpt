2026-05-19 | 10:48 UTC | Guard worker payload parse and deadletter malformed queue items | Bad payloads are deadlettered when run_id is resolvable, always acked, and worker loop continues.
2026-05-19 | 10:52 UTC | guard malformed payloads in recovery pass | Added parse guard+deadletter+ack in _recover_processing_queue_once for corrupted processing queue entries.
