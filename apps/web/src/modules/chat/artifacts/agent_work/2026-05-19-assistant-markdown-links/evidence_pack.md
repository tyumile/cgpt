# Evidence Pack

## 1. Changed files (`git diff --name-only`)
Global workspace is pre-dirty. Command output:
- `apps/api/app/db/main.py`
- `apps/api/app/modules/chats/main.py`
- `apps/api/app/modules/messages/main.py`
- `apps/api/app/modules/realtime/main.py`
- `apps/api/app/modules/worker_poller/main.py`
- `apps/api/tests/test_messages_chat_autotitle.py`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_bootstrap/main.ts`
- `commits.md`

Scoped files touched by this task:
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat/markdown.tsx` (new)
- `apps/web/src/modules/chat/commit.md` (new)
- `apps/web/src/modules/chat/artifacts/agent_work/2026-05-19-assistant-markdown-links/*` (new)
- `commits.md`

## 2. Diff summary (`git diff --stat`)
Global command output is pre-dirty and includes unrelated API work.

Scoped stats for this task:
- `apps/web/src/modules/chat/main.tsx | 7 ++++++-`
- `/dev/null => apps/web/src/modules/chat/markdown.tsx | 235 +++++++++++++++++++++`
- `/dev/null => apps/web/src/modules/chat/commit.md | 1 +`
- `commits.md | +1 line`

## 3. Exact behavior changed (before / after)
- Before: chat message body always rendered plain text; markdown markers remained visible and links were not clickable.
- After: assistant messages render through safe markdown renderer with clickable markdown links and bare URLs; links open in new tab with `noopener noreferrer`; user/system messages remain plain text.

## 4. Tests added or updated
- No automated tests added (no existing frontend test harness in this module).

## 5. Commands run
- `cd /srv/projects/aicom/cgpt/apps/web && npm run build`
- `cd /srv/projects/aicom/cgpt && git diff --name-only`
- `cd /srv/projects/aicom/cgpt && git diff --stat`
- `cd /srv/projects/aicom/cgpt && git diff --check`
- `cd /srv/projects/aicom/cgpt && git status --short -- apps/web/src/modules/chat commits.md`
- `cd /srv/projects/aicom/cgpt && git diff --name-only -- apps/web/src/modules/chat/main.tsx apps/web/src/modules/chat/markdown.tsx`
- `cd /srv/projects/aicom/cgpt && git diff --stat -- apps/web/src/modules/chat/main.tsx apps/web/src/modules/chat/markdown.tsx`
- `cd /srv/projects/aicom/cgpt && git diff --no-index --stat /dev/null apps/web/src/modules/chat/markdown.tsx`
- `cd /srv/projects/aicom/cgpt && git diff --no-index --stat /dev/null apps/web/src/modules/chat/commit.md`
- `rg -n "dangerouslySetInnerHTML|target=\"_blank\"|renderAssistantMarkdown" /srv/projects/aicom/cgpt/apps/web/src/modules/chat`

## 6. Results
- Build: PASS.
- Type checks during build: PASS.
- Diff gate (`git diff --check`): PASS.
- Safety checks: PASS (`dangerouslySetInnerHTML` absent, safe link attrs present).

## 7. Manual verification
- NOT VERIFIED: browser-based click-through and visual rendering check not executed in CLI environment.

## 8. Not verified
- Live UI manual confirmation for exact visual parity with chatgpt.com markdown rendering.

## 9. Risks
- Renderer is intentionally minimal and may not match full CommonMark/GFM edge-cases.
- Streaming partial markdown may transiently display intermediate formatting.

## 10. commit.md entry
- `apps/web/src/modules/chat/commit.md:1`
  - `2026-05-19 | 10:59 UTC | Assistant markdown + clickable links | Added safe markdown rendering for assistant role only with autolink and new-tab link policy.`
- `/srv/projects/aicom/cgpt/commits.md:44`
  - `2026-05-19 | 10:59 UTC | Assistant markdown rendering in chat | Assistant answers now render markdown with clickable links (including bare URLs) in chat module only.`
