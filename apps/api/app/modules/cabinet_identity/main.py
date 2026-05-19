import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.modules.cabinet_session.main import SESSION_TTL
from app.shared.schemas import CabinetAuthRequest, CabinetAuthResponse

router = APIRouter(prefix="/api/cabinet", tags=["cabinet_identity"])


@router.post("/auth", response_model=CabinetAuthResponse)
async def create_or_login_cabinet_user(
    payload: CabinetAuthRequest,
    session: AsyncSession = Depends(get_session),
) -> CabinetAuthResponse:
    email = payload.email.strip().lower()
    full_name = payload.full_name.strip()

    if not email or "@" not in email:
        raise HTTPException(status_code=422, detail="Invalid email")
    if not full_name:
        raise HTTPException(status_code=422, detail="Invalid full_name")

    user_row = (
        await session.execute(
            text(
                """
                INSERT INTO cabinet_users (email, full_name, created_at, updated_at)
                VALUES (:email, :full_name, now(), now())
                ON CONFLICT (email)
                DO UPDATE SET full_name = EXCLUDED.full_name, updated_at = now()
                RETURNING id, email, full_name
                """
            ),
            {"email": email, "full_name": full_name},
        )
    ).mappings().one()

    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    authorized_at = datetime.now(timezone.utc)
    expires_at = authorized_at + SESSION_TTL

    await session.execute(
        text(
            """
            INSERT INTO cabinet_sessions (user_id, token_hash, last_seen_at, created_at)
            VALUES (:user_id, :token_hash, :authorized_at, :authorized_at)
            """
        ),
        {
            "user_id": int(user_row["id"]),
            "token_hash": token_hash,
            "authorized_at": authorized_at,
        },
    )
    await session.execute(text("DELETE FROM cabinet_sessions WHERE created_at <= now() - interval '7 days'"))

    await session.commit()

    return CabinetAuthResponse(
        user_id=int(user_row["id"]),
        email=user_row["email"],
        full_name=user_row["full_name"],
        session_token=raw_token,
        expires_at=expires_at,
    )
