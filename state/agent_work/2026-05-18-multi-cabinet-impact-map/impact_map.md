# Impact Map: Multi-cabinet users + per-cabinet chat history + ChatGPT-like left sidebar

## 1. User-visible behavior
Users should be able to:
- create a cabinet account with `email` and `full_name` (name+surname),
- open chat under a cabinet identity,
- see only their own chat history,
- use a left sidebar showing chat history (ChatGPT-like),
- switch/open chats from the sidebar with isolated message history.

## 2. Current behavior
- Chat creation/list/get in `chats` module uses `X-Cabinet-Session` and scopes chats by `chat.user_id`.
- Message APIs (`/api/chats/{id}/messages`) do not validate cabinet session and do not scope by `user_id`.
- WebSocket endpoint (`/ws/chats/{chat_id}`) is unauthenticated and chat-id scoped only.
- Frontend has no explicit cabinet login/create flow and no left sidebar.
- Route `/chat/new` currently reuses first existing chat if present, instead of always creating a new chat.
- Alembic files in repo stop at `0002`, while runtime DB is on `0003_cabinet_identity_and_files` with extra tables/constraints.

## 3. Expected behavior
- Cabinet onboarding endpoint exists: create/find user by email + full name, issue session token.
- Session token is passed by frontend on all chat/message calls and WS connection.
- Chat list/get/create and message list/post are all consistently user-scoped.
- WS stream is user-scoped (reject cross-user chat subscription attempts).
- Left sidebar shows only current cabinet's chats, sorted by latest activity.
- `/chat/new` creates a new chat (or explicit UX decision documented if different).

## 4. Full pipeline / flow
input -> validation -> transform -> business logic -> storage -> API -> UI -> logs/errors

- Input:
  - Cabinet create/login form (`email`, `full_name`) from UI.
  - Chat open/new actions and message send actions.
  - WS connect request.
- Validation:
  - Email format, non-empty full_name.
  - Session token presence/validity.
  - Access check: `chat.user_id == session.user_id` before message/WS operations.
- Transform:
  - Session token -> SHA256 token_hash lookup.
  - Route params (`chat_id`) normalized in frontend/bootstrap.
- Business logic:
  - Issue cabinet session on auth endpoint.
  - Create/list/get chats per user.
  - Create/list messages only inside owned chat.
  - Publish realtime only to authorized subscribers.
- Storage:
  - `cabinet_users`, `cabinet_sessions`, `chats.user_id` used as source of truth.
  - Potentially update `chats.updated_at` when new message is posted (for sidebar order).
- API:
  - New cabinet auth endpoint(s).
  - Existing chats/messages/ws hardened for user scope.
- UI:
  - Add left sidebar with chat list and "new chat" action.
  - Preserve current chat screen and streaming behavior.
- Logs/errors:
  - 401 for missing/invalid session.
  - 403/404 for forbidden chat access.
  - UI error state for auth/session expiration.

## 5. Entry points
Backend:
- `apps/api/app/modules/chats/main.py`
- `apps/api/app/modules/messages/main.py`
- `apps/api/app/modules/realtime/main.py`
- `apps/api/app/main.py` (router registration)

Frontend:
- `apps/web/src/app/chat/[id]/page.tsx`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_bootstrap/main.ts`
- `apps/web/src/modules/api_client/main.ts`
- `apps/web/src/modules/realtime/main.ts`
- `apps/web/src/app/layout.tsx` (global shell potential)

## 6. Affected files
Directly affected by behavior change (expected):
- `apps/api/app/modules/chats/main.py`
- `apps/api/app/modules/messages/main.py`
- `apps/api/app/modules/realtime/main.py`
- `apps/api/app/db/models.py`
- `apps/api/app/shared/schemas.py`
- `apps/api/app/main.py`
- `apps/api/alembic/versions/*` (add missing cabinet-aware migration chain)
- `apps/web/src/modules/api_client/main.ts`
- `apps/web/src/app/chat/[id]/page.tsx`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_bootstrap/main.ts`
- new sidebar module(s), e.g. `apps/web/src/modules/chat_history/*`
- `apps/web/src/shared/types.ts`

## 7. Similar / duplicated logic
- Session resolution currently exists only in `chats` module via local helper; similar check must be centralized and reused in `messages` and `realtime`.
- Chat ownership check duplicated risk across endpoints (`get_chat`, `list_messages`, `post_message`, `ws connect`).
- Frontend data fetch logic for chats/messages is split between `chat_bootstrap` and `chat` page; sidebar introduces another consumer of `listChats`.

## 8. Call sites / consumers
- Frontend consumers of chats API:
  - `chat_bootstrap/main.ts` (`listChats`, `createChat`, `getChat`)
- Frontend consumers of messages API:
  - `chat/[id]/page.tsx` (`loadInitialMessages`)
  - `chat/main.tsx` (`postMessage`)
- Frontend consumer of WS:
  - `chat/main.tsx` through `realtime/main.ts`
- Backend downstream:
  - message posting creates runs and queues worker jobs; access checks must happen before run enqueue.

## 9. Invariants
- A cabinet user can access only own chats/messages/ws streams.
- Existing run pipeline (`agent_runs`, queue, worker, assistant finalize) remains functionally unchanged for authorized chats.
- Public API contract changes must be mirrored in frontend client.
- DB migration chain in repo must match runtime schema to avoid drift.

## 10. Required changes
- Add/restore canonical Alembic migration(s) for cabinet identity and `chats.user_id` (repo currently missing revision `0003_cabinet_identity_and_files`).
- Introduce shared auth/session resolver dependency (not local helper in one module).
- Apply resolver to:
  - chats routes (already partial),
  - messages routes (missing),
  - websocket connect path (missing).
- Ensure chat ownership checks on message list/post and ws connect.
- Add cabinet create/login endpoint contract (email + full_name) and return session token.
- Frontend:
  - store/pass cabinet session token on all API calls + WS,
  - add left sidebar component with chat list and create/open actions,
  - adjust `/chat/new` semantics to explicit "new chat" behavior,
  - preserve optimistic message + streaming UX.
- Optional but likely needed for sidebar ordering:
  - bump `chats.updated_at` on message post / assistant finalization.

## 11. Verification plan
Backend:
- Create cabinet user/session via new endpoint.
- Verify chat list/create/get is user-scoped.
- Verify messages list/post reject foreign chat ids.
- Verify ws connect rejects unauthorized chat ids.
- Verify run pipeline still completes for authorized chats.

Frontend:
- Login/create cabinet flow obtains session token.
- Sidebar renders own chats only.
- Open chat from sidebar loads correct history.
- New chat appears in sidebar and becomes active.
- Cross-cabinet isolation manual test with two sessions.

Schema/ops:
- Alembic upgrade on clean DB reaches head without missing revisions.
- Existing DB with `0003` remains compatible.

## 12. Exact search evidence
Commands executed:
- `rg --files`
- `cat docs/module_chain.md`
- `cat apps/api/app/modules/chats/AGENTS.md`
- `cat apps/web/src/modules/chat/AGENTS.md`
- `cat apps/web/src/modules/chat_bootstrap/AGENTS.md`
- `rg -n "cabinet|session|user_id|uploaded_files|/api/chats|/api/auth|login|register|sidebar|chat list|history" apps/api apps/web docs`
- `sed -n '1,260p' apps/api/app/main.py`
- `sed -n '1,280p' apps/api/app/db/models.py`
- `sed -n '1,260p' apps/web/src/modules/chat/main.tsx`
- `sed -n '1,260p' apps/web/src/modules/chat_bootstrap/main.ts`
- `cat docs/architecture.md`
- `cat docs/module_boundaries.md`
- `cat docs/stage1_acceptance.md`
- `sed -n '1,260p' apps/web/src/app/chat/[id]/page.tsx`
- `sed -n '1,220p' apps/web/src/app/layout.tsx`
- `sed -n '1,220p' apps/web/src/app/page.tsx`
- `sed -n '1,260p' apps/web/src/modules/api_client/main.ts`
- `sed -n '1,260p' apps/web/src/shared/types.ts`
- `sed -n '1,320p' apps/api/app/modules/messages/main.py`
- `sed -n '1,260p' apps/api/app/modules/messages_store/main.py`
- `sed -n '1,220p' apps/api/app/shared/schemas.py`
- `sed -n '1,280p' apps/api/app/modules/realtime/main.py`
- `sed -n '1,220p' apps/api/app/modules/run_enqueuer/main.py`
- `sed -n '1,260p' apps/api/app/modules/agent_exec/main.py`
- `sed -n '1,220p' apps/web/src/modules/realtime/main.ts`
- `sed -n '1,220p' apps/web/src/modules/messages/main.ts`
- `sed -n '1,320p' apps/api/alembic/versions/0001_stage1_schema.py`
- `sed -n '1,320p' apps/api/alembic/versions/0002_queue_worker_fields.py`
- `ls -la apps/api/alembic/versions`
- `psql 'postgresql://cgpt:cgpt@127.0.0.1:5432/cgpt' -c "select version_num from alembic_version;"`
- `psql 'postgresql://cgpt:cgpt@127.0.0.1:5432/cgpt' -c "\d+ chats"`
- `psql 'postgresql://cgpt:cgpt@127.0.0.1:5432/cgpt' -c "\d+ uploaded_files"`
- `psql 'postgresql://cgpt:cgpt@127.0.0.1:5432/cgpt' -c "\d+ cabinet_users"`
- `psql 'postgresql://cgpt:cgpt@127.0.0.1:5432/cgpt' -c "\d+ cabinet_sessions"`

Subagent evidence:
- Frontend explorer report (agent `019e3aea-8b8e-7a11-8efd-eb2b70faf217`).
- Backend explorer report (agent `019e3aea-8b00-77a0-a36b-5fb754a4e1a1`).
