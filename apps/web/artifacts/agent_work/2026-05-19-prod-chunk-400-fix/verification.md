# Verification

## Commands run
- `curl -sv https://aiaicom.ru/gpt/_next/static/chunks/app/chat/%5Bid%5D/page-8e4151c126cc0e3e.js`
- `curl http://127.0.0.1:13000/gpt/chat/new`
- `systemctl cat cgpt-web.service`
- `systemctl restart cgpt-web.service`
- `curl http://127.0.0.1:13000/gpt/chat/new`
- `curl https://aiaicom.ru/gpt/chat/new`
- `curl -I https://aiaicom.ru/gpt/_next/static/chunks/app/chat/%5Bid%5D/page-5bd9683536f4f198.js`
- production verification subagent run (Playwright)

## Results
- Pre-restart: stale chunk `page-8e4151c126cc0e3e.js` returned 400 and UI stuck.
- Post-restart: referenced chunk switched to `page-5bd9683536f4f198.js`, URL returns 200.
- Independent production verification subagent: PASS (desktop/mobile/auth/layout/readability checks).
