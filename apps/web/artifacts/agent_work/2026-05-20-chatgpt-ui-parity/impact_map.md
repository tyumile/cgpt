# Impact Map

## 1. User-visible behavior
- User wants chat UI to look and feel like ChatGPT web: layout proportions, sidebar behavior, composer placement, message cards, and subtle motion.

## 2. Current behavior
- Inline-styled MVP UI with basic blocks and minimal visual hierarchy.
- Mixed language labels and non-unified spacing/typography.
- Fixed message area height (`60vh`) and simple form row.

## 3. Expected behavior
- ChatGPT-like light UI:
  - Left sidebar with compact chat list and mobile sheet behavior.
  - Main thread area with assistant/user bubble separation.
  - Bottom sticky composer with attachment chip list.
  - Minimal transitions (sidebar slide, hover/focus states, message fade-in).
- No new controls for model/tools/search/pin.

## 4. Full pipeline / flow
- input: user text + file attachments in composer
- validation: empty input, file pick limits, send-disable states
- transform: optimistic message + ws chunk merge
- business logic: existing post/list/ws flow unchanged
- storage: unchanged (backend only)
- API: unchanged contracts for chats/messages/files
- UI: redesigned shell/sidebar/thread/composer only
- logs/errors: existing UI error surfacing retained and restyled

## 5. Entry points
- `apps/web/src/app/chat/[id]/page.tsx`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_history/main.tsx`
- `apps/web/src/app/layout.tsx`

## 6. Affected files
- `apps/web/src/app/layout.tsx`
- `apps/web/src/app/chat/[id]/page.tsx`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_history/main.tsx`
- `apps/web/src/modules/chat/markdown.tsx`
- new shared style file(s) under `apps/web/src/app/`

## 7. Similar / duplicated logic
- Repeated inline button/input containers across chat page and modules.
- Duplicate loading/error visual patterns with inconsistent styles.

## 8. Call sites / consumers
- `ChatPage` composes `ChatHistorySidebar` and `ChatScreen`.
- `ChatScreen` consumes `api_client`, `messages`, `realtime` modules.
- `ChatHistorySidebar` consumes list and delete operations via `api_client` and page callbacks.

## 9. Invariants
- Keep API endpoints and payload shapes unchanged.
- Keep websocket events and reducer behavior unchanged.
- Keep attachment upload/download flow intact.
- Maintain module boundaries inside web app.

## 10. Required changes
- Introduce CSS variables and shared classes for consistent tokens.
- Replace inline-heavy layout with semantic containers and class-based styling.
- Add lightweight motion and improved responsive behavior.
- Add RU/EN copy alignment for newly introduced labels.

## 11. Verification plan
- Static checks: lint/build.
- Manual flow:
  - open `/chat/new`
  - create/select chat via sidebar
  - send text message
  - attach file + send
  - observe thinking/streaming/done states
  - mobile width sidebar open/close and chat switch
- Diff gates: name-only/stat/check.

## 12. Exact search evidence
```bash
cat /srv/projects/aicom/cgpt/AGENTS.md
cat /srv/projects/aicom/AGENTS.md
find /srv/projects -maxdepth 3 -name AGENTS.md -print
cat /srv/projects/aicom/cgpt/docs/module_chain.md
cat /srv/projects/aicom/cgpt/docs/module_boundaries.md
rg --files /srv/projects/aicom/cgpt/apps/web/src
cat /srv/projects/aicom/cgpt/apps/web/src/app/chat/[id]/page.tsx
cat /srv/projects/aicom/cgpt/apps/web/src/modules/chat/main.tsx
cat /srv/projects/aicom/cgpt/apps/web/src/modules/chat_history/main.tsx
cat /srv/projects/aicom/cgpt/apps/web/src/modules/messages/main.ts
cat /srv/projects/aicom/cgpt/apps/web/src/modules/realtime/main.ts
cat /srv/projects/aicom/cgpt/apps/web/src/modules/api_client/main.ts
cat /srv/projects/aicom/cgpt/apps/web/src/modules/chat/markdown.tsx
rg -n "style=\{\{|Loading|Загрузка|Агент думает|New chat|Скрепка|Отправить|Удалить" /srv/projects/aicom/cgpt/apps/web/src
rg -n "connectChatWs|reduceWsEvent|postMessageWithAttachments|listMessages|ChatHistorySidebar|ChatScreen" /srv/projects/aicom/cgpt/apps/web/src -g '*.{ts,tsx}'
rg -n "fontFamily|background|borderRadius|transition|transform|matchMedia" /srv/projects/aicom/cgpt/apps/web/src -g '*.{ts,tsx}'
```
