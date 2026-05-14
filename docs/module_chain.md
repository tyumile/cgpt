# Stage 1 MVP Module Chain

## Numbering rule
- Numbering follows the runtime process path.
- If a module branches into two downstream modules, downstream IDs extend the parent path.
- One module = one function.

## Chain Tree
1. `1` Frontend Chat Interface (`apps/web/src/modules/chat/main.tsx`)
- Function: render chat screen, input, send button, loading/error states.
- Output A: sanitized user text to `1.2`.
- Output B: active chat subscription intent to `1.3`.

2. `1.2` Frontend API Client (`apps/web/src/modules/api_client/main.ts`)
- Function: call `POST /api/chats/{chat_id}/messages`.
- Input: user message from `1`.
- Output: `{message_id, agent_run_id}` to `1.3` and `1.5`.

3. `1.3` Frontend Realtime Client (`apps/web/src/modules/realtime/main.ts`)
- Function: open/reconnect WebSocket (`3 retries`) for current chat and consume events.
- Input: chat id from `1`, run ids from `1.2`.
- Output: stream events to `1.4`.

4. `1.4` Frontend Messages View Model (`apps/web/src/modules/messages/main.ts`)
- Function: merge persisted history + stream chunks (`chunk + full_text`) into UI message list.
- Input: initial history from `1.5`, stream events from `1.3`.
- Output: rendered state back to `1`.

5. `1.5` Frontend Chat Bootstrap (`apps/web/src/modules/chat_bootstrap/main.ts`)
- Function: open `/chat/[id]`, create first chat if none, load messages.
- Input: route state.
- Output: active `chat_id`, initial history to `1` and `1.4`.

6. `1.2.6` API Messages Endpoint (`apps/api/app/modules/messages/main.py`)
- Function: handle `POST /api/chats/{chat_id}/messages`; persist user message; create run.
- Input: HTTP payload from `1.2`.
- Output: persisted ids + background run trigger to `1.2.6.9`.

7. `1.2.6.7` Messages Storage (`apps/api/app/modules/messages_store/main.py`)
- Function: store user/assistant messages and streaming status transitions.
- Input: data from `1.2.6`, `1.2.6.9.12`.
- Output: message rows for DB and API reads.

8. `1.2.6.8` Agent Runs Registry (`apps/api/app/modules/agent_runs/main.py`)
- Function: create/update run (`queued/running/done/failed`), bind trigger/output messages.
- Input: run events from `1.2.6` and processing pipeline.
- Output: run lifecycle state for API and realtime.

9. `1.2.6.9` Agent Run Orchestrator (`apps/api/app/modules/agent_exec/main.py`)
- Function: execute Stage 1 pipeline after POST returns quickly.
- Input: `{workspace_id, chat_id, trigger_message_id, agent_run_id}` from `1.2.6`.
- Output A: stream events to `1.2.6.9.13`.
- Output B: final assistant text to `1.2.6.9.12`.

10. `1.2.6.9.10` Prompt Builder (`apps/api/app/modules/prompt_builder/main.py`)
- Function: compose system instruction + last 30 messages + workspace path.
- Input: chat context from `1.2.6.7`, workspace from `1.2.6.9.11`.
- Output: prompt text to `1.2.6.9.11`.

11. `1.2.6.9.11` Workspace Resolver (`apps/api/app/modules/workspaces/main.py`)
- Function: ensure `default` workspace exists and return root path.
- Input: request for workspace context.
- Output: workspace root (`runtime/workspaces/default`) to `1.2.6.9.10` and `1.2.6.9.14`.

12. `1.2.6.9.12` Assistant Finalizer (`apps/api/app/modules/assistant_finalize/main.py`)
- Function: persist final assistant message and mark run complete/failed.
- Input: final text/error from `1.2.6.9.14`.
- Output: DB state for history reload and UI consistency.

13. `1.2.6.9.13` Realtime Publisher (`apps/api/app/modules/realtime/main.py`)
- Function: broadcast JSON events `agent_run_started`, `assistant_chunk`, `assistant_done`, `assistant_error`.
- Input: run lifecycle and stream chunks from `1.2.6.9` / `1.2.6.9.14`.
- Output: WS events to frontend `1.3`.

14. `1.2.6.9.14` Codex Runner (`apps/api/app/modules/codex_runner/main.py`)
- Function: run `codex exec` under current user in workspace dir, timeout 10 minutes, stream stdout/stderr.
- Input: prompt from `1.2.6.9.10`, workspace path from `1.2.6.9.11`.
- Output: chunks and final text/error to `1.2.6.9` and `1.2.6.9.12`.

15. `1.6` Chats API (`apps/api/app/modules/chats/main.py`)
- Function: create/list/get chat and feed frontend route bootstrap.
- Input: requests from frontend bootstrap path.
- Output: chat metadata to `1.5`.

16. `1.7` Health API (`apps/api/app/modules/health/main.py`)
- Function: provide liveness endpoint.
- Output: `/health` status for ops and compose checks.

## Mandatory module folder contract
For each module folder:
1. `AGENTS.md` (required)
- Role: `You are the developer of this module`.
- Module task.
- Output contract (what this module passes to downstream modules).
- Mandatory reading links:
  - `/srv/projects/aicom/cgpt/AGENTS.md`
  - `/srv/projects/aicom/AGENTS.md`

2. Key implementation file
- Backend: `main.py`.
- Frontend: one key entry file (recommended `main.ts` or `main.tsx`), plus optional supporting files.
