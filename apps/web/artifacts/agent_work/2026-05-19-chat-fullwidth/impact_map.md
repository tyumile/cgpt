# Impact Map

## 1. User-visible behavior
Current chat pane is visually clipped by centered max-width containers. Requirement: fill all available horizontal space between left chat list and right viewport edge, while keeping readable max width for message text. On mobile, sidebar must hide and open via button.

## 2. Current behavior
- page-level loading/error shells use `maxWidth: 900` and centered layout.
- chat module root container uses `maxWidth: 900` and centered layout.
- sidebar has fixed width/minWidth and is always visible.

## 3. Expected behavior
- chat pane container uses full available width on desktop.
- message text/content column remains readability-constrained.
- loading/error states inherit full-width pane behavior.
- on mobile, sidebar is hidden by default and toggled by button.

## 4. Full pipeline / flow
input -> viewport width + route state
validation -> none new (UI-only layout logic)
transform -> compute responsive style toggles
business logic -> page shell composes sidebar + pane + toggle state
storage -> no change
API -> no change
UI -> layout and responsive behavior changed
logs/errors -> existing error text preserved; render width changes only

## 5. Entry points
- apps/web/src/app/chat/[id]/page.tsx
- apps/web/src/modules/chat/main.tsx
- apps/web/src/modules/chat_history/main.tsx

## 6. Affected files
- apps/web/src/app/chat/[id]/page.tsx
- apps/web/src/modules/chat/main.tsx
- apps/web/src/modules/chat_history/main.tsx

## 7. Similar / duplicated logic
Duplicated `maxWidth: 900` constraints exist both in chat page shell and chat screen module; both must be updated to avoid inconsistent states.

## 8. Call sites / consumers
- `ChatScreen` consumed by page shell only.
- `ChatHistorySidebar` consumed by page shell only.
- No backend/API consumers for this UI contract.

## 9. Invariants
- sidebar chat switching + create chat remains unchanged.
- send message + websocket stream remains unchanged.
- no API payload/headers/contracts changed.
- no global styling changes outside chat route shell.

## 10. Required changes
- remove pane-level fixed width constraints.
- add mobile sidebar toggle state and close interactions.
- keep readable text max-width in message rows.
- normalize loading/error wrappers to full-width pane.

## 11. Verification plan
- static checks: lint + build.
- manual checks at common widths: desktop and mobile.
- behavior checks: loading state, error state, message send/stream, sidebar open/close, chat switch.

## 12. Exact search evidence
Commands run:
- rg -n "maxWidth:\\s*900|width:\\s*300|minWidth:\\s*260" /srv/projects/aicom/cgpt/apps/web/src
- rg -n "ChatScreen|ChatHistorySidebar|/chat/\\[id\\]" /srv/projects/aicom/cgpt/apps/web/src
- sed -n '1,240p' /srv/projects/aicom/cgpt/apps/web/src/app/chat/[id]/page.tsx
- sed -n '1,260p' /srv/projects/aicom/cgpt/apps/web/src/modules/chat/main.tsx
- sed -n '1,260p' /srv/projects/aicom/cgpt/apps/web/src/modules/chat_history/main.tsx
