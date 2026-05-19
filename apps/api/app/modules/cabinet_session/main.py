import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import HTTPException, Request
from fastapi.websockets import WebSocket
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SESSION_HEADER = "x-cabinet-session"
SESSION_TTL = timedelta(days=7)


@dataclass(slots=True)
class CabinetSessionContext:
    session_id: int
    user_id: int
    expires_at: datetime


async def _resolve_session_context(session: AsyncSession, raw_token: str | None) -> CabinetSessionContext:
    if not raw_token:
        raise HTTPException(status_code=401, detail="Missing cabinet session")

    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    row = (
        await session.execute(
            text(
                """
                SELECT id, user_id, created_at
                FROM cabinet_sessions
                WHERE token_hash = :token_hash
                  AND created_at > now() - interval '7 days'
                LIMIT 1
                """
            ),
            {"token_hash": token_hash},
        )
    ).mappings().one_or_none()

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid cabinet session")

    await session.execute(
        text("UPDATE cabinet_sessions SET last_seen_at = now() WHERE id = :session_id"),
        {"session_id": int(row["id"])},
    )

    return CabinetSessionContext(
        session_id=int(row["id"]),
        user_id=int(row["user_id"]),
        expires_at=row["created_at"] + SESSION_TTL,
    )


async def resolve_cabinet_session_from_request(request: Request, session: AsyncSession) -> CabinetSessionContext:
    raw_token = request.headers.get(SESSION_HEADER)
    return await _resolve_session_context(session, raw_token)


async def resolve_cabinet_session_from_websocket(websocket: WebSocket, session: AsyncSession) -> CabinetSessionContext:
    raw_token = websocket.query_params.get("session_token")
    return await _resolve_session_context(session, raw_token)
