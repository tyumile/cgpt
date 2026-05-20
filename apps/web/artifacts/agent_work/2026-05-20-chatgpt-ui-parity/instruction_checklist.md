# Instruction Checklist

## Active rule sources
- System + developer session policies
- `/srv/projects/aicom/cgpt/AGENTS.md`
- Effective parent policy discovered at `/srv/projects/aicom/AGENTS.md` (path referenced in local AGENTS `/srv/projects/AGENTS.md` is missing)
- Frontend module AGENTS:
  - `/srv/projects/aicom/cgpt/apps/web/src/modules/chat/AGENTS.md`
  - `/srv/projects/aicom/cgpt/apps/web/src/modules/chat_history/AGENTS.md`
  - `/srv/projects/aicom/cgpt/apps/web/src/modules/chat_bootstrap/AGENTS.md`
  - `/srv/projects/aicom/cgpt/apps/web/src/modules/messages/AGENTS.md`
  - `/srv/projects/aicom/cgpt/apps/web/src/modules/realtime/AGENTS.md`

## Required specs/docs read
- `/srv/projects/aicom/cgpt/docs/module_chain.md`
- `/srv/projects/aicom/cgpt/docs/module_boundaries.md`
- Official UI references (OpenAI Help Center):
  - ChatGPT release notes
  - ChatGPT Search
  - Chat history search
  - ChatGPT home page
  - Model selector docs

## Scope in
- `apps/web` chat UI layer only:
  - chat page shell
  - chat history sidebar
  - messages view/composer
  - app-level styling for chat route
- RU/EN text alignment for new UI strings

## Scope out
- Backend/API contracts
- Model picker/tools/search/pinned chat features
- Auth flow behavior changes
- New product capabilities beyond current API

## Required verification commands
- `npm run lint` (if configured)
- `npm run build` (web)
- `git diff --name-only`
- `git diff --stat`
- `git diff --check`

## Required review types
- Plan review (local independent checklist against impact/extended plan)
- Result verification review (local evidence challenge)

## Explicit Definition of Done
- Chat UI becomes visually close to ChatGPT web in light theme with minimal animations.
- No API/ws flow regressions for send/stream/history/sidebar mobile open-close.
- No backend contract changes.
- Workflow artifacts and evidence pack created.
- `apps/web/commit.md` and root `commits.md` updated with UTC entries.
