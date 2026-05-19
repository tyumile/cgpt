# Impact Map

## 1. User-visible behavior
Users on `https://aiaicom.ru/gpt` were stuck on `Loading...` because chat page chunk request returned `400`.

## 2. Current behavior
Before fix, HTML referenced stale chunk `page-8e4151c126cc0e3e.js`; requesting that URL returned Next.js `400` error page.

## 3. Expected behavior
Production should reference current chunk hash, and chunk URL should return `200` so UI hydrates.

## 4. Full pipeline / flow
input -> browser requests `/gpt/chat/new`
validation -> Next runtime resolves build manifest entries
transform -> HTML emits chunk script URLs
business logic -> service process loads static build metadata on startup
storage -> `.next` artifacts on disk
API -> unchanged
UI -> hydration succeeds when chunk URL valid
logs/errors -> 400 error disappears

## 5. Entry points
- `/etc/systemd/system/cgpt-web.service`
- running process `next start -H 127.0.0.1 -p 13000`
- nginx route `/gpt/` -> `127.0.0.1:13000`

## 6. Affected files
- No source-code files changed for fix.
- runtime/service state changed by restarting `cgpt-web.service`.

## 7. Similar / duplicated logic
- Any future rebuild without restarting `cgpt-web` can recreate stale in-memory manifest mismatch.

## 8. Call sites / consumers
- External users of `/gpt` UI
- Nginx proxy consumer of `cgpt-web` service

## 9. Invariants
- API/WS endpoints remain on `18000` unchanged.
- Nginx routing rules remain unchanged.

## 10. Required changes
- Restart `cgpt-web.service` to reload current `.next` build metadata.

## 11. Verification plan
- Compare referenced chunk hash before/after restart.
- Verify old stale chunk no longer referenced.
- Verify referenced current chunk returns 200.
- Run production UI check via subagent with desktop+mobile coverage.

## 12. Exact search evidence
- `curl -sv https://aiaicom.ru/gpt/_next/static/chunks/app/chat/%5Bid%5D/page-8e4151c126cc0e3e.js`
- `curl http://127.0.0.1:13000/gpt/chat/new`
- `systemctl cat cgpt-web.service`
- `systemctl restart cgpt-web.service`
- `curl https://aiaicom.ru/gpt/chat/new`
