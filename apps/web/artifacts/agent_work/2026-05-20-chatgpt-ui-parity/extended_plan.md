# Extended Plan

## 1. Same bug class search
- Find other inline-style-heavy surfaces under `apps/web/src/app` and `apps/web/src/modules/*` that can cause inconsistent visual behavior.

## 2. Adjacent surfaces to inspect
- Auth card surface in chat page.
- Markdown rendering blocks in assistant responses.
- Error/loading hints across page/sidebar/thread.

## 3. Compatibility checks
- Ensure class-based refactor does not break Next.js client rendering.
- Ensure no dependency on unsupported CSS features in target browsers.

## 4. Persisted state checks
- Confirm chat list/message history loading still reflects backend persisted data.
- Confirm optimistic message replacement path still works after style refactor.

## 5. Additional protections
- Keep logic diffs minimal; avoid touching API, reducers, ws protocol.
- Add explicit disabled/button classes for pending states to prevent double-submits/deletes.

## 6. Additional tests
- Manual mobile viewport test for sidebar overlay/close controls.
- Manual attachment send + download button visual behavior.

## 7. Non-goals
- No implementation of model picker, tools menu, search sidebar, pinning.
- No backend changes.
- No dark theme in this task.

## 8. Final implementation boundary
- Frontend web files only inside `apps/web/src` and `apps/web/commit.md`, plus root `commits.md` task log entry.
