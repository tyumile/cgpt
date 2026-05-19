# Extended Plan

## 1. Same bug class search
- Find all backend surfaces that access chats/messages by `chat_id` without user ownership checks.
- Find all frontend network paths not attaching cabinet token.

## 2. Adjacent surfaces to inspect
- `agent_exec`/run queue payloads to ensure no user leakage.
- `messages_store` data access helpers for chat-id-only queries.
- ws reconnect path in frontend for missing token after page reload.

## 3. Compatibility checks
- WS auth uses query `session_token` only for this task; REST keeps `X-Cabinet-Session` header.
- New frontend token-based path does not break current `/gpt` proxying.

## 4. Persisted state checks
- Token persistence with 7-day expiry in browser storage.
- Session expiry enforcement from `created_at` in DB.

## 5. Additional protections
- Centralized resolver to avoid duplicated auth logic drift.
- Strict 401 on missing/invalid/expired token.

## 6. Additional tests
- Expired token rejected.
- Foreign chat id rejected in messages endpoint.
- WS denied when token missing/invalid or chat foreign.

## 7. Non-goals
- No password auth.
- No logout endpoint.
- No chat rename/delete.
- No redesign of chat message pane.

## 8. Final implementation boundary
- Only modules required for auth/session scope, sidebar history, and migration alignment.
- Preserve existing agent execution pipeline semantics.
