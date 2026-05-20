2026-05-19 | 10:48 UTC | Ensure last_seen_at persistence in session resolver | Added explicit commit after last_seen_at update in auth/session resolve flow.
2026-05-19 | 10:52 UTC | make session touch transaction-safe | Removed inline resolver commit; rely on request dependency commit and websocket-side commit to avoid breaking enclosing transactions.
