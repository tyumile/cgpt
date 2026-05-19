# Extended Plan

## 1. Same bug class search
Search for other hardcoded width caps in chat route and related modules (`maxWidth`, fixed px pane width, centered wrappers).

## 2. Adjacent surfaces to inspect
- auth-required state view in chat page
- loading and error placeholders
- sidebar create/switch controls after responsive changes

## 3. Compatibility checks
- desktop: sidebar visible + full-width pane
- mobile: toggle open/close + overlay dismiss
- no contract changes with API/ws modules

## 4. Persisted state checks
No persisted state migration required. Keep existing session/chat/message persistence untouched.

## 5. Additional protections
- close sidebar on mobile after selecting a chat.
- close sidebar when switching from mobile to desktop width.

## 6. Additional tests
No automated UI tests available; cover with lint/build and explicit manual checks documented in verification report.

## 7. Non-goals
- redesign typography/theme
- backend changes
- route/auth flow redesign

## 8. Final implementation boundary
Only the three targeted frontend files are modified.
