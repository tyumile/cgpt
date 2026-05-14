# Architecture

Stage 1.5 request pipeline:
1. Frontend sends message.
2. API stores user message, creates `agent_run(status=queued)`, enqueues job to Redis.
3. Worker consumes queue, claims run lease, builds prompt, runs codex.
4. Worker publishes stream events to Redis pub/sub.
5. API realtime bridge forwards pub/sub events to websocket clients.
6. Final assistant message is persisted and run marked `done`/`failed`.

## Runtime boundaries
- Codex executes only inside `runtime/workspaces/default`.
- API and worker run as current user with mounted `~/.codex`.
- No auth, billing, queue sharding, multi-agent orchestration in this stage.
