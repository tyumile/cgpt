# Evidence Pack

## 1) Changed files (`git diff --name-only`)
Repository currently has pre-existing unrelated modifications. Task-targeted changes were implemented in:
- `apps/api/app/main.py`
- `apps/api/app/modules/cabinet_identity/main.py` (new)
- `apps/api/app/modules/cabinet_identity/AGENTS.md` (new)
- `apps/api/app/modules/cabinet_session/main.py` (new)
- `apps/api/app/modules/cabinet_session/AGENTS.md` (new)
- `apps/api/app/modules/chats/main.py`
- `apps/api/app/modules/messages/main.py`
- `apps/api/app/modules/messages_store/main.py`
- `apps/api/app/modules/realtime/main.py`
- `apps/api/app/shared/schemas.py`
- `apps/api/alembic/versions/0003_cabinet_identity_and_files.py` (new)
- `apps/web/src/modules/cabinet_auth/main.ts` (new)
- `apps/web/src/modules/cabinet_auth/AGENTS.md` (new)
- `apps/web/src/modules/chat_history/main.tsx` (new)
- `apps/web/src/modules/chat_history/AGENTS.md` (new)
- `apps/web/src/modules/api_client/main.ts`
- `apps/web/src/modules/realtime/main.ts`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_bootstrap/main.ts`
- `apps/web/src/app/chat/[id]/page.tsx`
- `apps/web/src/shared/types.ts`
- `apps/api/app/db/models.py`
- `docs/module_chain.md`
- `commits.md`

Out-of-repo operational change required for multi-cabinet runtime:
- `/etc/nginx/sites-available/aiaicom.ru` (removed hardcoded cabinet session forwarding; now forwards incoming `X-Cabinet-Session`).

## 2) Diff summary (`git diff --stat`)
- Current diff summary includes unrelated pre-existing files in repository.
- Task-targeted files listed above contain the implemented behavior changes.

## 3) Exact behavior changed (before/after)
- Before:
  - No cabinet auth endpoint.
  - Partial user scoping only in chats; messages/ws not strictly protected.
  - Frontend generated local fake token and had no true backend auth handshake.
  - No left chat-history sidebar.
  - `/chat/new` reused first chat.
  - Nginx forced one static cabinet session for all public `/gpt` requests.
- After:
  - `POST /api/cabinet/auth` implemented (email duplicate => login, else create), session token issued.
  - Session validated with strict 7-day TTL from authorization time.
  - Chats/messages/ws enforce cabinet session and ownership checks.
  - Frontend authenticates against backend, persists session token for 7 days, and sends token on REST + WS.
  - Left sidebar shows per-user chat list with first-message preview.
  - `/chat/new` always creates a new chat.
  - Nginx forwards caller session header instead of hardcoded token, enabling real multi-cabinet behavior on `https://aiaicom.ru/gpt`.

## 4) Tests added/updated
- No new automated tests added in this task.
- Existing backend test suite still passes.

## 5) Commands run
- `PYTHONPATH=/srv/projects/aicom/cgpt/apps/api /srv/projects/aicom/cgpt/.venv/bin/python -m pytest -q` (apps/api)
- `npm run build` (apps/web)
- `/srv/projects/aicom/cgpt/.venv/bin/python -m compileall apps/api/app apps/api/alembic/versions/0003_cabinet_identity_and_files.py`
- service restart via PID TERM for `cgpt-api`, `cgpt-worker`, `cgpt-web` and systemd auto-restart verification
- runtime smoke via `curl` for auth/chats/messages and ownership isolation
- runtime ws smoke via Python `websockets`
- `git diff --name-only`
- `git diff --stat`
- `git diff --check`

## 6) Results
- Backend tests: `9 passed`.
- Frontend build: success (Next.js production build complete).
- Compile checks: success.
- Runtime:
  - `/gpt/health` => 200.
  - auth endpoint returns token + expiry ~7 days ahead.
  - missing token on chats => 401.
  - foreign chat access => 404.
  - own ws connect => success.
  - missing/foreign ws connect => rejected (403 handshake from FastAPI).

## 7) Manual verification
- Verified with two different cabinet sessions that chat lists are isolated.
- Verified preview field appears after first message in chat.
- Verified `/gpt` stack services are active after restart.

## 8) Not verified
- Full browser-side UX walkthrough with visual confirmation in GUI was not executed in this terminal-only run.

## 9) Risks
- Existing repository has unrelated pre-existing modified files; commit isolation must be done carefully.
- ORM still does not model `cabinet_users/cabinet_sessions/uploaded_files`; future Alembic autogenerate may need extra care.
- No new dedicated unit/integration tests for cabinet auth/sidebar flows yet.

## 10) `commits.md` entry
- `- 2026-05-18 | 12:31 UTC | Multi-cabinet auth + per-user history + sidebar implementation | Added cabinet auth/session flow, strict REST/WS ownership checks, frontend sidebar/history with 7-day persisted sessions, and reconciled /gpt proxy header behavior for multi-user routing.`
