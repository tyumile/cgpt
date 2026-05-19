# Implementation Plan

## 1. Root cause
`cgpt-web` process held stale in-memory build references (old chunk hash), while `.next` artifacts on disk were newer.

## 2. Change strategy
Apply minimal systemic fix at runtime layer: restart only `cgpt-web.service` to synchronize running Next process with current build artifacts.

## 3. File-by-file plan
- No code file edits.
- Service operation: `systemctl restart cgpt-web.service`.

## 4. Layer coverage
- input: browser page request
- validation/transform: Next runtime chunk resolution
- business logic: process-level build manifest lifecycle
- storage: `.next` build artifacts consistency with runtime process
- API/UI/contracts: no API contract changes

## 5. Test plan
- chunk URL status checks before and after restart
- production UI verification by subagent

## 6. Verification commands
- `systemctl status cgpt-web.service`
- `curl https://aiaicom.ru/gpt/chat/new`
- `curl -I https://aiaicom.ru/gpt/_next/static/chunks/app/chat/%5Bid%5D/<chunk>.js`

## 7. Risks
- brief restart window can produce transient `502`.

## 8. Done when
- current chunk from `/gpt/chat/new` returns `200`
- production UI verification returns PASS
