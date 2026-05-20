# Evidence Pack
## Changed files (global workspace)
- Obtained via `git diff --name-only` in `/srv/projects/aicom/cgpt`.
- Workspace contains pre-existing unrelated modifications; only the feature-relevant files were edited for this task.

## Diff summary
- Obtained via `git diff --stat`.
- Includes unrelated pre-existing modified files in addition to this task scope.

## Exact behavior changed
Before:
- Chat accepted JSON-only messages; no file attachments.
- No attachment metadata in message history.
- No file download endpoint.
- Agent prompt had no trigger attachment paths.

After:
- Chat uses multipart message endpoint (`content` + `files`) with limits and executable-type blocking.
- Files saved on disk under `uploads/user_<id>/chat_<id>/...` and persisted in `uploaded_files`.
- Message history includes attachment metadata and download path.
- Download endpoint with ownership/workspace path checks.
- Agent prompt includes latest message attachment absolute paths and per-user upload root.
- Chat deletion removes uploaded files from DB and disk.
- UI renders attachment list in user bubble and reconciles optimistic rows after send.

## Tests added/updated
- `apps/api/tests/test_messages_chat_autotitle.py` updated for multipart contract and new validation semantics.
- `apps/api/tests/test_chats_delete.py` updated for file-cleanup query/mapping behavior.
- `apps/api/tests/test_prompt_builder.py` added prompt attachment/root assertions.

## Commands run
- `cd /srv/projects/aicom/cgpt/apps/api && PYTHONPATH=/srv/projects/aicom/cgpt/apps/api /srv/projects/aicom/cgpt/.venv/bin/pytest`
- `cd /srv/projects/aicom/cgpt/apps/web && npm run build`
- `cd /srv/projects/aicom/cgpt && git diff --name-only`
- `cd /srv/projects/aicom/cgpt && git diff --stat`
- `cd /srv/projects/aicom/cgpt && git diff --check`

## Results
- API tests: `18 passed`.
- Web build: successful.
- Independent verification subagent: final status `PASS`.

## Manual verification
- Not executed against running browser session in this task turn.

## Not verified
- End-to-end browser interaction with real uploads/download clicks in a live session.

## Risks
- Upload MIME detection depends on client-provided `content_type`; extension deny-list is the primary executable guard.
- Existing pre-dirty workspace may contain unrelated behavior changes outside this task.

## commit.md entries
- Added entries in:
  - `apps/api/app/modules/messages/commit.md`
  - `apps/api/app/modules/messages_store/commit.md`
  - `apps/api/app/modules/chats/commit.md`
  - `apps/api/app/modules/agent_exec/commit.md`
  - `apps/api/app/modules/prompt_builder/commit.md`
  - `apps/web/src/modules/api_client/commit.md`
  - `apps/web/src/modules/chat/commit.md`
  - `apps/web/src/modules/messages/commit.md`
