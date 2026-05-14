# Stage 1 Acceptance

## Implemented
- Modular backend and frontend structure.
- PostgreSQL persistence for workspaces/chats/messages/agent_runs.
- Redis queue + dedicated worker for run processing.
- WebSocket events: `agent_run_started`, `assistant_chunk`, `assistant_done`, `assistant_error`.
- Message history persists across reload.
- Graceful codex CLI error handling.
- Docker Compose primary run path.

## Out of scope (not implemented)
- Auth, billing, roles, companies, file upload, admin, vector memory, complex orchestration.
