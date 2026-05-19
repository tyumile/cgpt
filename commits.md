# Commits Log

- 2026-05-14 | 10:54 UTC | Stage 1 module chain + local AGENTS rule | Added project AGENTS rules, created process-chain module tree, initialized commits log.
- 2026-05-14 | 11:09 UTC | Stage 1 MVP implementation | Implemented modular FastAPI+Next.js chat MVP with Postgres persistence, websocket streaming, codex runner, docs, and compose setup.
- 2026-05-14 | 11:22 UTC | Live E2E docker production fix | Fixed codex exec flags, deployed docker stack, verified websocket stream to assistant_done on public endpoint.
2026-05-14 | 11:36 UTC | Independent review: Redis queue + worker implementation plan | Reported ISSUES with blocking gaps and hardening additions.
- 2026-05-14 | 12:04 UTC | Standalone git init for GitHub publish | Ignored runtime state, created local commit, and prepared `tyumile/cgpt` push target.
- 2026-05-14 | 12:46 UTC | Queue worker resilience follow-up | Added atomic run claim, processing-queue recovery, regression tests, and verified compose recovery path.
- 2026-05-15 | 12:23 UTC | Update AGENTS top-level policy link | Repointed policy references to /srv/projects/AGENTS.md and removed outdated missing-path note.
- 2026-05-15 | 12:58 UTC | Expose cgpt on /gpt via nginx + basePath | Updated web basePath/public endpoints, configured /gpt proxy with cabinet session header, verified external /gpt and /gpt/api access.
- 2026-05-18 | 11:20 UTC | Restore /gpt runtime + cabinet-aware chat create | Rebuilt missing .venv for cgpt services, restored api/worker, added cabinet session user resolution for chats, verified /gpt health/list/create endpoints.
- 2026-05-18 | 11:50 UTC | Backend audit for multi-cabinet surfaces | Mapped current schema/API, user/session scoping entry points, and migration/contract risks for cabinet/chats/messages/files.
- 2026-05-18 | 11:53 UTC | Multi-cabinet impact map | Prepared impact map + checklist artifacts and implementation planning questions.
- 2026-05-18 | 12:31 UTC | Multi-cabinet auth + per-user history + sidebar implementation | Added cabinet auth/session flow, strict REST/WS ownership checks, frontend sidebar/history with 7-day persisted sessions, and reconciled /gpt proxy header behavior for multi-user routing.
- 2026-05-18 | 12:38 UTC | External verifier clickthrough for /gpt chat UI | Browser automation blocked by missing system libs; completed HTTP/API fallback verification with evidence artifacts and documented unverified visual surfaces.
2026-05-18 | 12:57 UTC | UI clickthrough regression recheck + optimistic preview hardening | Immediate preview fixed in browser checks; blocking assistant-response 504 remains
2026-05-18 | 13:04 UTC | External UI clickthrough recheck (WS fallback) | BLOCKING ISSUES: assistant timeout and 504 reproduced on /gpt/api/chats/{id}/messages
2026-05-18 | 13:08 UTC | Third external UI clickthrough after websocket session handling fix | PASS: assistant response received, no 504 on messages endpoints, session/history persisted
2026-05-18 | 13:09 UTC | Fix intermittent 504 on /gpt/api/chats/{id}/messages | Moved websocket auth/ownership DB checks to short-lived session before subscribe; removed long-lived DB session from ws lifecycle; external clickthrough PASS
- 2026-05-19 | 05:10 UTC | Commit and push yesterday changes | Bundled pending 2026-05-18 updates into one git commit and pushed to origin/main.
2026-05-19 | 05:21 UTC | Chat UI full-width impact map | Reviewed AGENTS/workflow, mapped width constraints and downstream impacts, prepared clarification questions.
2026-05-19 | 05:30 UTC | Прочтение AGENTS и формулировка роли | Локальный и общий AGENTS прочитаны, роль и задача сформулированы.
2026-05-19 | 05:32 UTC | Показ общего AGENTS с переводом | Выведен полный текст общего AGENTS и дан русскоязычный перевод терминов.
2026-05-19 | 05:34 UTC | Вывод общего AGENTS полностью на русском | Подготовлен текст политики без англоязычных формулировок.
2026-05-19 | 05:39 UTC | Добавление workflow-правил в AGENTS | В локальный AGENTS добавлены 3 правила: изоляция субагентов, точечные изменения по ТЗ, frontend-проверка отдельным субагентом.
2026-05-19 | 05:39 UTC | Production UI verification for https://aiaicom.ru/gpt | Blocked: app stuck on Loading due Next chunk 400, target checks unverified
2026-05-19 | 05:46 UTC | Final production UI recheck on https://aiaicom.ru/gpt | BLOCKING ISSUES confirmed on desktop/mobile: stuck Loading, Next chunk /gpt/_next/static/chunks/app/chat/%5Bid%5D/page-8e4151c126cc0e3e.js returns 400
2026-05-19 | 05:48 UTC | Chat full-width UI implementation via subagents | Implemented pane-width and mobile sidebar behavior; build PASS; production verification blocked by remote Next chunk 400.
2026-05-19 | 06:04 UTC | Production UI verification after runtime fix on https://aiaicom.ru/gpt | PASS: no chunk 400 Loading lock; desktop/mobile/sidebar/readability checks verified with Playwright evidence
2026-05-19 | 06:06 UTC | Resolve /gpt chunk 400 via cgpt-web restart | Restarted stale Next process; production chunk now 200 and UI verification PASS.
2026-05-19 | 06:38 UTC | Add 2% chat pane side offsets | Added 2% horizontal padding for chat pane section and fixed width overflow with border-box/minWidth guards.
2026-05-19 | 06:41 UTC | Recover gray /gpt screen (chunk mismatch) | Restarted cgpt-web after .next hash drift; production chunk resolved and UI bootstrap restored.
2026-05-19 | 06:45 UTC | Quick production visual check for /gpt hydration | PASS: auth UI rendered after 15s; no console errors, no failed requests, no HTTP 4xx/5xx (no chunk 400).
2026-05-19 | 09:45 UTC | Restore production /gpt frontend chunk delivery | Restarted cgpt-web runtime process to resync Next build manifest; critical chat page chunk now 200 and /gpt,/gpt/chat/new client boot verified.
2026-05-19 | 10:04 UTC | Production browser delete-flow verification on /gpt | PASS for auth/create/non-active+active delete and /chat/empty redirect; found MAJOR layout overlap, no blocking console/network errors.
2026-05-19 | 10:07 UTC | Recheck production /gpt delete UI + layout after overlap fix | PASS: non-active/active delete flow works, /chat/empty redirect works, no key 4xx/5xx, aside-section overlap resolved on desktop.
2026-05-19 | 10:07 UTC | Chat deletion (UI+API+DB) with uploaded_files cleanup | Added DELETE /api/chats/{id}, marks queued/running runs failed, deletes uploaded_files/agent_runs/messages/chat, sidebar delete UX, /chat/empty flow, tests+build PASS.
2026-05-19 | 10:07 UTC | Production verification and runtime recovery for /gpt chat delete flow | Resynced cgpt-web/cgpt-api runtimes, fixed chunk 400 and API 405, independent UI recheck PASS (delete non-active/active chat, /chat/empty, no overlap).
2026-05-19 | 10:28 UTC | Chat auto-title from first user message | New chats default to "Новый чат"; first user message sets sanitized title once; second messages do not overwrite; API/Web checks and production verification PASS.
