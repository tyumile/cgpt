# Impact Map
## User-visible behavior
- Chat input has attachment picker (paperclip workflow).
- Message send uploads files and text together.
- User sees attachment list inside own message bubble with download links.
- Agent can access uploaded files from workspace path on request.

## Current behavior
- POST /api/chats/{chat_id}/messages accepts JSON content only.
- uploaded_files table exists in DB migration, but no ORM/service usage.
- No file download route and no attachment fields in message responses.

## Expected behavior
- POST /api/chats/{chat_id}/messages accepts multipart form-data.
- Enforce limits: max 10 files, max 20MB each, block executable/script-like files.
- Store files under workspace/uploads/user_<user_id>/chat_<chat_id>/ and persist metadata.
- Include attachment metadata in message response/history.
- Add download endpoint with ownership check.
- Agent prompt includes attachment paths and user upload root path.

## Full pipeline
input -> frontend FormData + files
validation -> API text required + size/count/type/name/path checks
transform -> sanitized/stored file names + relative path
business logic -> create message, store files, create run, enqueue
storage -> disk write + uploaded_files rows + existing messages/runs
API -> multipart POST + GET attachment download + GET messages enriched
UI -> bubble attachment list + send-file UX/errors
logs/errors -> clear validation/rejection reasons

## Entry points
- apps/web/src/modules/chat/main.tsx
- apps/web/src/modules/api_client/main.ts
- apps/api/app/modules/messages/main.py
- apps/api/app/modules/messages_store/main.py
- apps/api/app/modules/agent_exec/main.py
- apps/api/app/modules/prompt_builder/main.py
- apps/api/app/modules/chats/main.py

## Invariants
- Files must remain within workspace root.
- User can only operate within owned chat.
- Trigger message attachments map to that message only.
- Chat deletion removes file records and physical files.

## Verification plan
- API tests for title flow with new multipart endpoint.
- API tests for chat delete include file deletion path handling.
- Prompt builder tests for attachment context.
- Full api pytest and web build.

## Exact search evidence
- rg -n "attachment|file upload|multipart|UploadFile|FormData|/messages|workspace" /srv/projects/aicom/cgpt/apps -S
- rg -n "uploaded_files|relative_path|mime_type|size_bytes" /srv/projects/aicom/cgpt/apps/api -S
- sed -n on messages/chat/prompt_builder/agent_exec/codex_runner/web chat modules and migrations.
