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
