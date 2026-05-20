# Implementation Plan

## 1. Root cause
The chat UI renders message content as plain text only. Markdown is never parsed, and URLs are not transformed into anchor tags.

## 2. Change strategy
Implement a self-contained, safe markdown renderer inside `chat` module and switch only assistant message body to this renderer. Keep non-assistant rendering unchanged.

## 3. File-by-file plan
- `apps/web/src/modules/chat/markdown.tsx` (new)
  - Add lightweight parser/renderer for base markdown features:
    - paragraphs and line breaks
    - unordered lists (`-` / `*`)
    - fenced code blocks (```)
    - inline code (`code`)
    - bold (`**...**`)
    - emphasis (`*...*`)
    - markdown links (`[text](https://...)`)
    - bare URL autolink (`https://...`)
  - Normalize bare URLs by trimming trailing punctuation from href detection.
  - Disallow raw HTML execution by construction (React text nodes only, no `dangerouslySetInnerHTML`).
  - Render anchors with `target="_blank" rel="noopener noreferrer"`.
  - Keep malformed markdown link fragments as plain text.
- `apps/web/src/modules/chat/main.tsx`
  - Route assistant `message.content` through markdown renderer.
  - Keep user/system output in plain text mode.
  - Add minimal inline styles for markdown block readability.

## 4. Layer coverage
- input: unchanged
- validation: unchanged
- business logic: role-based render path in chat UI
- persistence: unchanged
- API/contract: unchanged
- UI: changed assistant message display
- tests: no existing frontend test harness; verify via build + manual checks
- logs/errors: unchanged
- docs: workflow artifacts + commit logs only

## 5. Test plan
- Build project successfully.
- Manual render checks for markdown + links.
- Manual regression for send/stream UI behavior.

## 6. Verification commands
- `cd /srv/projects/aicom/cgpt/apps/web && npm run build`
- `cd /srv/projects/aicom/cgpt && git diff --name-only`
- `cd /srv/projects/aicom/cgpt && git diff --stat`
- `cd /srv/projects/aicom/cgpt && git diff --check`

## 7. Risks
- Regex-based inline parsing can mishandle deeply nested markdown edge cases.
- Streaming partial markdown can briefly render intermediate formatting states.
- URL tokenization may incorrectly include punctuation if parser guards regress.

## 8. Done when
- Assistant markdown formatting and link clickability work in UI.
- Non-assistant messages remain plain text.
- No HTML execution path introduced.
- Build and diff gates pass.
- Task notes appended to module and global commit logs.
