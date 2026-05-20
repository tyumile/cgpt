# Evidence Pack

## 1. Changed files (`git diff --name-only`)
Repository-wide (includes pre-existing unrelated edits):
- `AGENTS.md`
- `apps/api/app/db/main.py`
- `apps/api/app/modules/realtime/main.py`
- `apps/api/app/modules/worker_poller/main.py`
- `apps/web/src/app/chat/[id]/page.tsx`
- `apps/web/src/app/layout.tsx`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_bootstrap/main.ts`
- `apps/web/src/modules/chat_history/main.tsx`
- `commits.md`

Task-scoped tracked diffs:
- `apps/web/src/app/chat/[id]/page.tsx`
- `apps/web/src/app/layout.tsx`
- `apps/web/src/modules/chat/main.tsx`
- `apps/web/src/modules/chat_history/main.tsx`

Task-scoped untracked files:
- `apps/web/src/app/chatgpt-ui.css`
- `apps/web/src/modules/chat/markdown.tsx`
- `apps/web/artifacts/agent_work/2026-05-20-chatgpt-ui-parity/*`

## 2. Diff summary (`git diff --stat`)
Task-scoped tracked summary:
- `apps/web/src/app/chat/[id]/page.tsx` | 132 lines changed
- `apps/web/src/app/layout.tsx` | 3 lines changed
- `apps/web/src/modules/chat/main.tsx` | 217 lines changed
- `apps/web/src/modules/chat_history/main.tsx` | 221 lines changed
- Total: 294 insertions, 279 deletions

## 3. Exact behavior changed (before / after)
- Before: MVP inline-style UI, basic containers, minimal hierarchy, fixed-height thread area.
- After: ChatGPT-like light UI structure with sidebar/thread/sticky composer, tokenized CSS design system, minimal motion, and RU/EN labels selected by browser language.

## 4. Tests added or updated
- No automated tests added/updated (UI-only refactor).

## 5. Commands run
- See `verification.md`.

## 6. Results
- Build: PASS.
- Lint: BLOCKED by interactive Next.js ESLint setup prompt.
- Diff checks: PASS for scoped files.

## 7. Manual verification
- NOT VERIFIED: interactive browser smoke checks were not executed in this run.

## 8. Not verified
- Desktop/mobile runtime visual parity confirmation in browser.
- Sidebar open/close UX and stream animation feel validation in real session.

## 9. Risks
- Repository lacks non-interactive lint path until ESLint config is committed.
- Visual parity is high-level; exact pixel-match may still require iterative tuning in browser.

## 10. commit.md entry
- `apps/web/commit.md` appended:
  - `2026-05-20 | 10:45 UTC | Chat UI redesign to ChatGPT-like light interface | Refactored chat page, sidebar, thread, and composer to class-based ChatGPT-style UI with minimal animations and RU/EN copy; web build PASS, lint blocked by interactive Next ESLint setup.`
- Root `commits.md` appended:
  - `2026-05-20 | 10:45 UTC | Chat UI redesign to ChatGPT-like light interface | Refactored web chat UI (shell/sidebar/thread/composer), added design tokens and RU/EN labels; build PASS, lint not runnable non-interactively due missing Next ESLint config prompt.`
