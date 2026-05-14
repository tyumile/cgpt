import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.main import get_settings
from app.db.main import AsyncSessionLocal, init_db
from app.modules.chats.main import router as chats_router
from app.modules.health.main import router as health_router
from app.modules.messages.main import router as messages_router
from app.modules.realtime.main import router as realtime_router
from app.modules.realtime.main import start_realtime_bridge, stop_realtime_bridge
from app.modules.workspaces.main import ensure_default_workspace
from app.shared.redis_client import close_redis

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SaaS Chat MVP API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(chats_router)
app.include_router(messages_router)
app.include_router(realtime_router)


@app.on_event("startup")
async def startup() -> None:
    settings = get_settings()
    await init_db()
    async with AsyncSessionLocal() as session:
        await ensure_default_workspace(session)

    if settings.app_role == "api":
        await start_realtime_bridge()


@app.on_event("shutdown")
async def shutdown() -> None:
    settings = get_settings()
    if settings.app_role == "api":
        await stop_realtime_bridge()
    await close_redis()
