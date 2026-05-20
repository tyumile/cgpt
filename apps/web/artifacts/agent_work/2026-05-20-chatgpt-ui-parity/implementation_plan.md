# Implementation Plan

## 1. Root cause
- UI assembled as MVP with inline styles and no shared design tokens, so visual parity with ChatGPT is structurally difficult.

## 2. Change strategy
- Keep behavior modules intact; redesign presentation layer with class-based CSS and small structural JSX updates.
- Prefer minimal-risk UI-only refactor without API/state semantics changes.

## 3. File-by-file plan
1. `src/app/layout.tsx`
- Attach global stylesheet and normalize body/root containers for full-height chat surface.

2. `src/app/chat/[id]/page.tsx`
- Replace inline shell/auth styles with class names.
- Keep auth and routing logic unchanged.

3. `src/modules/chat_history/main.tsx`
- Rebuild sidebar markup classes for desktop/mobile parity.
- Keep data loading, delete, and selection logic unchanged.

4. `src/modules/chat/main.tsx`
- Rebuild thread/composer markup classes.
- Add safe auto-scroll behavior and minimal animation classes.
- Preserve optimistic send, ws handling, attachments logic.

5. `src/modules/chat/markdown.tsx`
- Retune markdown block styles to match new surface tokens.

6. `src/app/chatgpt-ui.css` (new)
- Define tokens, typography, spacing, sidebar/thread/composer components, and minimal animations.

## 4. Layer coverage
- Input: unchanged behavior, improved controls states
- Validation: unchanged
- Business logic: unchanged
- Persistence: unchanged
- API/contract: unchanged
- UI: redesigned
- Tests: build/lint + manual smoke
- Logs/errors: same logic, restyled output
- Docs: evidence/plan artifacts

## 5. Test plan
- Build/lint checks in `apps/web`.
- Manual functional checks for send/stream/attachments/sidebar mobile.

## 6. Verification commands
```bash
cd /srv/projects/aicom/cgpt/apps/web
npm run lint
npm run build

cd /srv/projects/aicom/cgpt
git diff --name-only
git diff --stat
git diff --check
```

## 7. Risks
- Visual refactor may break mobile layout if class mapping incomplete.
- Auto-scroll behavior can feel jumpy if not gated to bottom-follow mode.
- Existing dirty worktree increases review noise.

## 8. Done when
- Chat route has ChatGPT-like light design and minimal motion.
- Existing message/chat workflows still operate.
- Verification commands pass or failures are documented honestly.
