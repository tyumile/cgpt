# Verification
## Commands
1. `cd /srv/projects/aicom/cgpt/apps/api && pytest` (failed in system python env: missing deps/PYTHONPATH)
2. `cd /srv/projects/aicom/cgpt/apps/api && PYTHONPATH=/srv/projects/aicom/cgpt/apps/api /srv/projects/aicom/cgpt/.venv/bin/pytest`
3. `cd /srv/projects/aicom/cgpt/apps/web && npm run build`
4. `cd /srv/projects/aicom/cgpt && git diff --name-only`
5. `cd /srv/projects/aicom/cgpt && git diff --stat`
6. `cd /srv/projects/aicom/cgpt && git diff --check`

## Results
- API tests: PASS (`18 passed`).
- Web build: PASS (`next build` completed successfully).
- Diff check: PASS (`git diff --check` no whitespace/conflict errors).

## Notes
- Repository is pre-dirty with unrelated modified/untracked files from prior work.
