2026-05-19 | 10:48 UTC | realtime subscriber resilience fix | Added reconnect/backoff loop, done()-task restart, and robust pubsub cleanup on cancel.
2026-05-19 | 10:52 UTC | persist websocket session touch safely | Commit session touch in WS auth path after ownership check to persist last_seen_at without resolver-side commit.
