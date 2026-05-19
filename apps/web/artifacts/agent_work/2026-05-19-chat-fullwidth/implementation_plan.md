# Implementation Plan

## 1. Root cause
Hardcoded centered containers (`maxWidth: 900`) constrain chat pane width. Sidebar has no responsive hide/show behavior and is always present.

## 2. Change strategy
Apply minimal systemic fix in three frontend files only:
- page shell owns mobile sidebar open/close state and layout orchestration.
- sidebar module receives visibility/toggle props.
- chat module removes pane-level cap and adds readable text max-width at message content level.

## 3. File-by-file plan
- apps/web/src/app/chat/[id]/page.tsx
  - add sidebar open state and mobile menu button in pane.
  - pass visibility/control props to sidebar.
  - remove loading/error max width constraints.
- apps/web/src/modules/chat_history/main.tsx
  - support responsive hidden/off-canvas mobile drawer.
  - add close button and overlay behavior.
  - keep desktop sidebar width adaptive: `clamp(260px, 22vw, 320px)`.
- apps/web/src/modules/chat/main.tsx
  - remove root `maxWidth` cap.
  - keep messages/input region full pane width.
  - constrain readable text line width only in message body.

## 4. Layer coverage
- input: viewport size + route state only
- validation: no new user input validation
- business logic: page shell state for sidebar visibility
- persistence: none
- API/contract: unchanged
- UI: layout and responsive behavior updated
- tests: no existing UI test harness; rely on lint/build + manual verification
- logs/errors: preserve text semantics
- docs: evidence artifacts only

## 5. Test plan
- run lint and build in apps/web.
- manual route checks on /chat/new and /chat/{id}.

## 6. Verification commands
- cd /srv/projects/aicom/cgpt/apps/web && npm run lint
- cd /srv/projects/aicom/cgpt/apps/web && npm run build
- git -C /srv/projects/aicom/cgpt diff --name-only
- git -C /srv/projects/aicom/cgpt diff --stat
- git -C /srv/projects/aicom/cgpt diff --check

## 7. Risks
- mobile overlay may block interactions if z-index ordering is wrong.
- keeping inline styles can increase verbosity and drift.
- SSR window checks must remain safe.

## 8. Done when
- pane is full-width on desktop with readable text cap only.
- sidebar hidden on mobile and controllable by button.
- loading/error panels full-width.
- no regressions in message send/stream/chat switching.


## 9. Post-completion logging
- Append one entry to `/srv/projects/aicom/cgpt/commits.md` in required UTC format after verification.
- If module-level `commit.md` is absent, create/update module log per parent policy within changed module scope.

## 10. Localization requirement
- Any newly introduced user-facing controls for this task must be in Russian.

## 11. Served-output verification
- Validate layout behavior in served app for widths: 390, 768, 1024, 1366, 1920.
- Validate mobile close paths: overlay click, close button, and chat-select auto-close.
- Validate no horizontal page scroll on mobile.
