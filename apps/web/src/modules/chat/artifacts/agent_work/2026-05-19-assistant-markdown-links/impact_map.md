# Impact Map

## 1. User-visible behavior
Assistant answers in chat currently appear as plain text; markdown markers are visible and links are not actionable. Required behavior: assistant answers render markdown and links are clickable.

## 2. Current behavior
- `apps/web/src/modules/chat/main.tsx` renders `message.content` inside `<div style={{ whiteSpace: "pre-wrap" }}>`.
- No markdown parser or linkification layer exists.
- All roles (`user`, `assistant`, `system`) share the same plain-text rendering path.

## 3. Expected behavior
- `assistant` role only: markdown rendering enabled with safe output (no raw HTML execution).
- Markdown links and bare URLs become clickable anchors.
- Links open in new tab with `target="_blank" rel="noopener noreferrer"`.
- `user` and `system` messages keep plain-text behavior.

## 4. Full pipeline / flow
`input` -> assistant produces markdown/plain URLs in text
`validation` -> no markdown validation (unchanged)
`transform` -> ws/history reducers keep raw string in `content` (unchanged)
`business logic` -> chat module chooses rendering strategy by message role (changed)
`storage` -> DB stores raw assistant text (unchanged)
`API` -> API returns raw string content (unchanged)
`UI` -> assistant text rendered with markdown/linkification (changed)
`logs/errors` -> unchanged error/reporting paths

## 5. Entry points
- `apps/web/src/modules/chat/main.tsx` (message presentation)

## 6. Affected files
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat/markdown.tsx` (new helper for parsing/rendering)
- `apps/web/src/modules/chat/commit.md` (task note)
- `/srv/projects/aicom/cgpt/commits.md` (task note)

## 7. Similar / duplicated logic
- `apps/web/src/modules/chat_history/main.tsx` has preview text stripping/ellipsis. It is intentionally plain text and out of scope.
- No second assistant message renderer found in `apps/web` search scope.

## 8. Call sites / consumers
- `apps/web/src/app/chat/[id]/page.tsx` consumes `ChatScreen`.
- Realtime (`assistant_chunk`, `assistant_done`) feeds `ChatScreen` via state, so renderer must support partial markdown safely.

## 9. Invariants
- Preserve `Message.content` as raw string across API/DB/UI state.
- Do not execute HTML from assistant output.
- Keep existing send/stream/retry flow unchanged.
- Keep role labels and error handling unchanged.

## 10. Required changes
- Add role-aware renderer in chat UI:
  - assistant -> markdown renderer with URL autolink
  - non-assistant -> plain-text renderer
- Add minimal markdown styling for readability (paragraphs, lists, code, blockquote, links).
- Enforce link safety attributes.

## 11. Verification plan
- Build gate: `cd /srv/projects/aicom/cgpt/apps/web && npm run build`
- Diff gates:
  - `git diff --name-only`
  - `git diff --stat`
  - `git diff --check`
- Manual UI checks:
  - bold/italic/list/code in assistant message
  - markdown link `[name](https://...)`
  - bare URL `https://...`
  - partial streaming markdown does not crash render
  - user message remains plain text

## 12. Exact search evidence
- `rg --files /srv/projects/aicom/cgpt | rg 'AGENTS\.md$'`
- `rg -n "markdown|md|render|message|link|sanitize|html|remark|react-markdown|dangerouslySetInnerHTML|auto.?link|url" /srv/projects/aicom/cgpt/apps/web /srv/projects/aicom/cgpt/apps/api --glob '!**/node_modules/**'`
- `sed -n '1,260p' /srv/projects/aicom/cgpt/apps/web/src/modules/chat/main.tsx`
- `sed -n '1,260p' /srv/projects/aicom/cgpt/apps/web/src/modules/messages/main.ts`
- `sed -n '1,380p' /srv/projects/aicom/cgpt/apps/web/src/modules/chat_history/main.tsx`
- `sed -n '1,340p' /srv/projects/aicom/cgpt/apps/web/src/app/chat/[id]/page.tsx`
- `cat /srv/projects/aicom/cgpt/apps/web/package.json`
