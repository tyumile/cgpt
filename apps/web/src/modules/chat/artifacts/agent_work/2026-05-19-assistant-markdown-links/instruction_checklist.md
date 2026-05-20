# Instruction Checklist

## Active Rule Sources
- `/srv/projects/aicom/cgpt/AGENTS.md`
- `/srv/projects/aicom/AGENTS.md`
- `/srv/projects/aicom/cgpt/apps/web/src/modules/chat/AGENTS.md`
- `/srv/projects/docs/code_review.md`
- `/srv/projects/docs/front_review.md`

## Required Specs/Docs Read
- `/srv/projects/aicom/cgpt/docs/module_chain.md`
- `/srv/projects/aicom/cgpt/docs/module_boundaries.md`
- NOTE: `/srv/projects/docs/test_review.md` is referenced by policy but absent in filesystem.

## Scope In
- `apps/web/src/modules/chat/main.tsx`
- New helper(s) only under `apps/web/src/modules/chat/`
- Module artifacts under `apps/web/src/modules/chat/artifacts/agent_work/2026-05-19-assistant-markdown-links/`
- Module task log `apps/web/src/modules/chat/commit.md` (create if missing)
- Global task log `/srv/projects/aicom/cgpt/commits.md`

## Scope Out
- API modules and DB schema/migrations
- `apps/web/src/modules/messages/*`
- `apps/web/src/modules/chat_history/*` behavior changes
- Any non-chat frontend modules

## Required Verification Commands
- `cd /srv/projects/aicom/cgpt/apps/web && npm run build`
- `cd /srv/projects/aicom/cgpt && git diff --name-only`
- `cd /srv/projects/aicom/cgpt && git diff --stat`
- `cd /srv/projects/aicom/cgpt && git diff --check`

## Required Review Types
- Code review checklist (`/srv/projects/docs/code_review.md`)
- Frontend review checklist (`/srv/projects/docs/front_review.md`)
- Local independent Plan Review (no subagents in this session)
- Local independent Result Verification (no subagents in this session)

## Definition Of Done (Task-Specific)
- Assistant messages render markdown formatting (without HTML execution).
- Markdown links and plain URLs are clickable and open in new tab with safe `rel`.
- User/system messages remain plain text output.
- Streaming assistant chunks remain stable and readable during partial markdown.
- Build passes and diff gates pass.
- `apps/web/src/modules/chat/commit.md` updated with UTC note.
- `/srv/projects/aicom/cgpt/commits.md` updated with UTC note.
