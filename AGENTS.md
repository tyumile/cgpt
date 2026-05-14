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
2. Parent policy: `/srv/projects/aicom/AGENTS.md`
3. Project docs and module docs inside this repository

Note:
- Requested path `/srv/projects/AGENTS.md` is currently missing in this environment.
- Until it exists, `/srv/projects/aicom/AGENTS.md` is the mandatory top-level policy source.

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
   - mandatory links to local project `AGENTS.md` and parent `/srv/projects/aicom/AGENTS.md`.

## Task Log Rule
After each completed task, append a concise entry to `/srv/projects/aicom/cgpt/commits.md` with:
- UTC date
- UTC time
- task title/summary
- short outcome

Format:
- `YYYY-MM-DD | HH:MM UTC | <task> | <result>`
