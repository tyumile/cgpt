# Implementation Plan

## 1. Root cause
- Multi-cabinet capability is partial and inconsistent:
  - chats endpoints are session-aware,
  - messages/ws are not session-scoped,
  - no cabinet auth endpoint in API/frontend.
- UI lacks chat-history sidebar and explicit cabinet onboarding flow.
- Alembic chain in repo misses runtime schema revision `0003_cabinet_identity_and_files`.

## 2. Change strategy
- Introduce explicit cabinet auth/session modules in backend.
- Centralize session resolution and reuse it in chats/messages/ws.
- Add missing Alembic `0003` migration to align repo with runtime DB.
- Add frontend cabinet bootstrap (email + full_name) with 7-day persisted token.
- Add left sidebar module for chat history and chat switching/creation.
- Keep chat message pane behavior and stream UX intact.

## 3. File-by-file plan
Backend:
- Add `apps/api/app/modules/cabinet_identity/main.py` (session issue endpoint).
- Add `apps/api/app/modules/cabinet_identity/AGENTS.md`.
- Add `apps/api/app/modules/cabinet_session/main.py` (token hash + resolve/validate user, 7-day TTL).
- Add `apps/api/app/modules/cabinet_session/AGENTS.md`.
- Update `apps/api/app/main.py` to include cabinet identity router.
- Update `apps/api/app/modules/chats/main.py` to consume shared session resolver and add preview-first-message field in responses.
- Update `apps/api/app/modules/messages/main.py` to enforce user-owned chat access.
- Update `apps/api/app/modules/realtime/main.py` to validate `session_token` + chat ownership before subscribe.
- Update `apps/api/app/shared/schemas.py` with cabinet auth schemas and optional chat preview.
- Add `apps/api/alembic/versions/0003_cabinet_identity_and_files.py`.

Frontend:
- Add `apps/web/src/modules/cabinet_auth/main.ts` (auth API call + token storage/ttl handling).
- Add `apps/web/src/modules/cabinet_auth/AGENTS.md`.
- Add `apps/web/src/modules/chat_history/main.tsx` (left sidebar list/create/switch).
- Add `apps/web/src/modules/chat_history/AGENTS.md`.
- Update `apps/web/src/modules/api_client/main.ts` to send `X-Cabinet-Session` on all chat/message calls.
- Update `apps/web/src/modules/realtime/main.ts` to pass token in ws URL query.
- Update `apps/web/src/modules/chat/main.tsx` minimally (token param for ws + optional callback hooks).
- Update `apps/web/src/modules/chat_bootstrap/main.ts` so `new` creates new chat.
- Update `apps/web/src/app/chat/[id]/page.tsx` to orchestrate cabinet form state + sidebar + current chat pane.
- Update `apps/web/src/shared/types.ts` for new response fields.

Docs/chain:
- Update `docs/module_chain.md` to include new modules and numbering continuity.

## 4. Layer coverage
- Input: cabinet auth form and session token propagation.
- Validation: email/full_name, token validity, token age <= 7 days, chat ownership.
- Business logic: upsert-by-email login/create + session issuance.
- Persistence: cabinet tables + chat scope + migration consistency.
- API contract: new cabinet endpoint and chat response preview field.
- UI: left sidebar with own history and preserved chat pane.
- Tests: add backend tests for auth/session and access scope.
- Logs/errors: structured 401/404 and ws close-on-auth-fail behavior.
- Docs: module chain update.

## 5. Test plan
- Unit tests for cabinet auth/session helpers.
- API tests for:
  - create/login by email,
  - chat/message access isolation,
  - session expiry behavior.
- Manual smoke:
  - login -> chat list visible,
  - create chat via sidebar,
  - switch chats,
  - message send/stream still works,
  - second user cannot access first user's chat via REST/WS.

## 6. Verification commands
- `python -m pytest -q` for targeted API tests.
- `curl` smoke:
  - cabinet auth endpoint,
  - `/gpt/api/chats`, `/gpt/api/chats/{id}/messages`,
  - ws handshake with/without token.
- `git diff --name-only`
- `git diff --stat`
- `git diff --check`

## 7. Risks
- Migration drift between existing prod DB and repo chain.
- WS auth semantics (close code behavior) across clients.
- Sidebar integration may accidentally change message pane behavior.

## 8. Done when
- Cabinet auth (email+full_name) issues reusable session token.
- Session valid for 7 days and enforced across chats/messages/ws.
- Chat history in left sidebar shows only current cabinet chats with first-message preview.
- `/chat/new` creates a new chat.
- Existing chat pane behavior (send/stream) remains intact.
- Alembic repo includes `0003` and can migrate clean DB to head.


## 9. Migration matrix
- Clean DB path:
  - Apply 0001 -> 0002 -> new 0003 (`0003_cabinet_identity_and_files`) to produce cabinet tables, `chats.user_id`, and `uploaded_files`.
- Existing DB path (already at `0003_cabinet_identity_and_files`):
  - New migration file must use idempotent DDL (`IF NOT EXISTS`/guarded constraints) and match same revision id so runtime and repo align.
- Head topology:
  - Single linear head at `0003_cabinet_identity_and_files`.
- Rollback stance:
  - No destructive rollback in this task; forward-only reconciliation.

## 10. WebSocket auth contract
- Accepted token location: query parameter `session_token` on `/ws/chats/{chat_id}`.
- Precedence: query parameter is authoritative (no header fallback in WS for this task).
- Validation failures:
  - Invalid/missing/expired token -> close code `1008` immediately.
  - Valid token but foreign chat ownership -> close code `1008`.
- Reconnect behavior:
  - Frontend retry logic remains, but invalid token should surface persistent error message to user.

## 11. Frontend verification commands
- `npm run lint` (or `npm run build` if lint unavailable) in `apps/web`.
- Manual smoke in browser:
  - auth form -> session persisted -> reload keeps cabinet for <7 days,
  - sidebar shows own chats,
  - `/chat/new` creates new chat,
  - switching sidebar chats loads correct history.
