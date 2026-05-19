# Evidence Pack

## Changed files
- No source-code files changed for incident fix.
- Runtime operation performed: `systemctl restart cgpt-web.service`.

## Runtime evidence
- Pre-fix failing chunk: `page-8e4151c126cc0e3e.js` -> 400.
- Post-fix active chunk: `page-5bd9683536f4f198.js` -> 200.

## Production verification artifacts
- `/srv/projects/aicom/state/agent_work/ui-prod-check-20260519T055521Z/verification_report.json`
- `/srv/projects/aicom/state/agent_work/ui-prod-check-20260519T055521Z/desktop_after_auth.png`
- `/srv/projects/aicom/state/agent_work/ui-prod-check-20260519T055521Z/desktop_after_message.png`
- `/srv/projects/aicom/state/agent_work/ui-prod-check-20260519T055521Z/mobile_default.png`
- `/srv/projects/aicom/state/agent_work/ui-prod-check-20260519T055521Z/mobile_sidebar_open.png`
- `/srv/projects/aicom/state/agent_work/ui-prod-check-20260519T055521Z/mobile_after_overlay_close.png`
- `/srv/projects/aicom/state/agent_work/ui-prod-check-20260519T055521Z/mobile_after_button_close.png`

## Not verified
- `npm run lint` remains interactive in this repo setup.
