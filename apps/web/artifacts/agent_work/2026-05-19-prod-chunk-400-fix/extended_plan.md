# Extended Plan

## 1. Same bug class search
Check for stale hash mismatch between HTML-emitted chunk and on-disk chunk names.

## 2. Adjacent surfaces to inspect
- nginx upstream reachability
- `cgpt-web.service` startup health

## 3. Compatibility checks
- `/gpt/api/*` and `/gpt/ws/*` unchanged
- only web process restart

## 4. Persisted state checks
No persisted data changes.

## 5. Additional protections
Recommend deployment hook: restart `cgpt-web.service` after each successful web build/deploy.

## 6. Additional tests
Subagent-driven desktop/mobile production check including auth and interaction.

## 7. Non-goals
- frontend code edits
- nginx config edits

## 8. Final implementation boundary
Runtime/service restart + verification only.
