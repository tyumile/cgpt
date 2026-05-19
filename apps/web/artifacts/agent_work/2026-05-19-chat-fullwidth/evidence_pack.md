# Evidence Pack

## 1. Changed files (git diff --name-only)
```
apps/web/src/app/chat/[id]/page.tsx
apps/web/src/modules/chat/main.tsx
apps/web/src/modules/chat_history/main.tsx
commits.md
```

## 2. Diff summary (git diff --stat)
```
apps/web/src/app/chat/[id]/page.tsx        |   6 +-
 apps/web/src/modules/chat/main.tsx         |   4 +-
 apps/web/src/modules/chat_history/main.tsx | 214 +++++++++++++++++++++--------
 commits.md                                 |   8 ++
 4 files changed, 171 insertions(+), 61 deletions(-)
```

## 3. Exact behavior changed
- Before: chat pane/loading/error states were width-capped by 900px wrappers; mobile sidebar lacked hide/show toggle behavior.
- After: chat pane and loading/error wrappers are full-width within the right pane; message text keeps readability cap (`72ch`); mobile sidebar is hidden by default and controlled by `Чаты`/overlay/`Закрыть`/chat-select close.

## 4. Tests added or updated
- None.

## 5. Commands run
- `git diff --name-only`
- `git diff --stat`
- `git diff --check`
- `cd apps/web && npm run build`
- `cd apps/web && npm run lint` (interactive blocked)
- production checks on `https://aiaicom.ru/gpt` via Playwright subagents

## 6. Results
- Build: PASS
- Lint: NOT VERIFIED (interactive ESLint init prompt)
- Independent result verification subagent: PASS (after mobile trigger out-of-flow fix)
- Production verification subagent: BLOCKING ISSUES (`/gpt/_next/static/chunks/app/chat/%5Bid%5D/page-8e4151c126cc0e3e.js` returns `400`)

## 7. Manual verification
- Source-level + diff-level review completed.
- Build output validated.
- Production browser automation evidence captured by subagent.

## 8. Not verified
- Local lint command in CI-like non-interactive mode (missing lint config; interactive prompt).
- Production functional UI behavior (blocked by remote asset error).

## 9. Risks
- Production deployment/runtime issue outside this local UI patch blocks live acceptance testing.

## 10. commit.md entry
- Added: `/srv/projects/aicom/cgpt/apps/web/commit.md`
- Added line in: `/srv/projects/aicom/cgpt/commits.md`

## Current git status
```
M apps/web/src/app/chat/[id]/page.tsx
 M apps/web/src/modules/chat/main.tsx
 M apps/web/src/modules/chat_history/main.tsx
 M commits.md
?? apps/web/artifacts/
?? apps/web/commit.md
```

## git diff --check
```
(no output)
```
