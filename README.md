# SaaS Chat MVP Stage 1

Minimal modular SaaS chat MVP with FastAPI, PostgreSQL, Next.js, WebSocket streaming, Redis queue worker, and local `codex exec` runtime.

## Stack
- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- DB: PostgreSQL + SQLAlchemy + Alembic
- Queue: Redis + worker service
- Realtime: WebSocket with Redis pub/sub bridge
- Runtime: local `codex exec`
- Dev deploy: Docker Compose

## Prerequisites
- Docker + Docker Compose
- Codex CLI installed on host and authenticated
- Host has `~/.codex` directory (mounted into API/worker containers)

## Quick Start
1. Copy env:
```bash
cp .env.example .env
```
2. Export current user ids (Linux):
```bash
export UID=$(id -u)
export GID=$(id -g)
```
3. Start:
```bash
docker compose up --build -d
```
4. Open web: `http://localhost:3000` (or port from `.env`).

## Services
- `db`: PostgreSQL
- `redis`: queue broker
- `migrate`: runs `alembic upgrade head`
- `api`: HTTP + WS fanout
- `worker`: queue consumer and codex executor
- `web`: Next.js UI

## API
- `GET /health`
- `POST /api/chats`
- `GET /api/chats`
- `GET /api/chats/{chat_id}`
- `GET /api/chats/{chat_id}/messages`
- `POST /api/chats/{chat_id}/messages`
- `WS /ws/chats/{chat_id}`

## Notes on Codex
- Runner uses `codex exec` with:
  - `--sandbox workspace-write`
  - `--skip-git-repo-check`
  - `--cd <workspace>`
- Timeout defaults to 600 seconds.
- All runs are restricted to `runtime/workspaces/default`.
