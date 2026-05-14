# Module Boundaries

## Backend
- `workspaces`: default workspace bootstrap and lookup
- `chats`: chat CRUD API
- `messages`: HTTP message endpoint + queue enqueue path
- `messages_store`: message persistence operations
- `agent_runs`: run lifecycle, lease, heartbeat, stale detection
- `prompt_builder`: codex prompt composition
- `codex_runner`: codex subprocess execution and streaming
- `agent_exec`: run execution pipeline
- `assistant_finalize`: final assistant message + status updates
- `realtime`: websocket endpoint and redis pub/sub fanout
- `run_enqueuer`: queue payload builder and enqueue
- `queue_meta`: run-to-job queue metadata sync
- `worker_poller`: redis queue consumer loop and reaper integration
- `run_retry`: transient error retry policy
- `run_deadletter`: terminal failure recording
- `health`: health endpoint

## Frontend
- `chat`: chat screen UI
- `chat_bootstrap`: chat routing/bootstrap logic
- `api_client`: HTTP client module
- `realtime`: websocket client module
- `messages`: stream + history state reducer
