---
metadata:
  artifact_root: /srv/projects/aicom/state/agent_work
---

# AGENTS.md

## Purpose
Local operating rules for `/srv/projects/aicom/cgpt`.
These rules extend and must not weaken parent repository policy.

## Mandatory Reading Chain
1. This file: `/srv/projects/aicom/cgpt/AGENTS.md`
2. Parent policy: `/srv/projects/AGENTS.md`
3. Project docs and module docs inside this repository

Note:
- Top-level policy source: `/srv/projects/AGENTS.md`.

## Core Implementation Rules
1. Build by modules with process-chain numbering.
2. One module owns one function.
3. Each module lives in its own folder.
4. For backend/service modules, keep one key file named `main.py`.
5. For UI modules, multiple files are allowed, but the module must still have one key entry file.
6. Each module must contain its own `AGENTS.md` with:
   - role: developer of this module;
   - module task;
   - output artifact/data passed to downstream modules;
   - mandatory links to local project `AGENTS.md` and parent `/srv/projects/AGENTS.md`.

## Task Log Rule
After each completed task, append a concise entry to `/srv/projects/aicom/cgpt/commits.md` with:
- UTC date
- UTC time
- task title/summary
- short outcome

Format:
- `YYYY-MM-DD | HH:MM UTC | <task> | <result>`

## GitHub Push Authentication Rule
1. For `git push` to GitHub, use SSH authentication by default.
2. Repository remote for push should use SSH form: `git@github.com:<org-or-user>/<repo>.git`.
3. Before push, verify SSH auth with:
   - `ssh -T git@github.com`
   - `ssh-add -l` (to check loaded keys)
4. SSH keys should be searched in the current user's SSH directory: `~/.ssh` (for example: `id_ed25519`, `id_rsa`, and `config`).
5. If remote is HTTPS, switch it to SSH before pushing:
   - `git remote set-url origin git@github.com:<org-or-user>/<repo>.git`

## Post-Deploy And Runtime Verification Rules
1. After web deploy/restart, verify:
   - `GET /gpt/chat/new` returns `200`.
   - all referenced `/gpt/_next/static/chunks/*.js` return `200` (no `400` chunk mismatch).
2. After API/worker deploy/restart, verify:
   - `GET /gpt/api/chats` returns `401` without session (service reachable).
   - authenticated `GET /gpt/api/chats` returns `200`.
3. Required service restarts after changes:
   - web changes: `sudo systemctl restart cgpt-web.service`
   - api changes: `sudo systemctl restart cgpt-api.service`
   - worker or run pipeline changes: `sudo systemctl restart cgpt-worker.service`
4. Mandatory attachment smoke test after attachment-related changes:
   - create session token
   - create chat
   - send `multipart/form-data` message with `content` + file
   - verify `POST /api/chats/{id}/messages` returns `200` with `message_id` and `agent_run_id`
   - verify `GET /api/chats/{id}/messages` returns user message with non-empty `attachments`
   - verify assistant message appears and can reference file content
5. Validation/contract rule for multipart endpoints:
   - client/input errors must return `4xx` (not `500`)
   - validation errors must be safely serializable (no raw binary payload in error body)

## Known Production Failure Modes
1. `Loading...` stuck on `/gpt` due Next chunk mismatch:
   - symptom: some `/gpt/_next/static/chunks/*.js` return `400`
   - fix: `sudo systemctl restart cgpt-web.service`, then re-check all chunk URLs from `/gpt/chat/new`
2. Agent cannot read files due sandbox namespace error:
   - symptom: `bwrap: Creating new namespace failed`
   - fix: ensure `CODEX_SANDBOX_MODE=danger-full-access` for `cgpt-api` and `cgpt-worker`, then restart both services
3. Multipart upload returns `500` due stale API process:
   - symptom: API still expects JSON body for `POST /api/chats/{id}/messages`
   - fix: restart `cgpt-api` and `cgpt-worker`, then re-run attachment smoke test
