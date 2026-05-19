import asyncio
import json
import logging
from collections import defaultdict

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.config.main import get_settings
from app.db.main import AsyncSessionLocal
from app.db.models import Chat
from app.modules.cabinet_session.main import resolve_cabinet_session_from_websocket
from app.shared.redis_client import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)


class RealtimeManager:
    def __init__(self) -> None:
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, chat_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.connections[chat_id].add(websocket)

    async def disconnect(self, chat_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            if chat_id in self.connections:
                self.connections[chat_id].discard(websocket)
                if not self.connections[chat_id]:
                    self.connections.pop(chat_id, None)

    async def broadcast(self, chat_id: int, event: dict) -> None:
        async with self._lock:
            targets = list(self.connections.get(chat_id, set()))
        for ws in targets:
            try:
                await ws.send_json(event)
            except Exception:
                await self.disconnect(chat_id, ws)


manager = RealtimeManager()
_subscriber_task: asyncio.Task | None = None


async def publish_event(chat_id: int, event: dict) -> None:
    settings = get_settings()
    redis = get_redis()
    payload = json.dumps({"chat_id": chat_id, "event": event}, ensure_ascii=False)
    await redis.publish(settings.run_events_channel, payload)


async def _subscriber_loop() -> None:
    settings = get_settings()
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(settings.run_events_channel)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                await asyncio.sleep(0.05)
                continue

            data = message.get("data")
            if not data:
                continue

            if isinstance(data, bytes):
                data = data.decode("utf-8", errors="ignore")

            payload = json.loads(data)
            await manager.broadcast(payload["chat_id"], payload["event"])
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Realtime subscriber loop failed")
    finally:
        await pubsub.unsubscribe(settings.run_events_channel)
        await pubsub.close()


async def start_realtime_bridge() -> None:
    global _subscriber_task
    if _subscriber_task is None:
        _subscriber_task = asyncio.create_task(_subscriber_loop())


async def stop_realtime_bridge() -> None:
    global _subscriber_task
    if _subscriber_task is not None:
        _subscriber_task.cancel()
        try:
            await _subscriber_task
        except asyncio.CancelledError:
            pass
        _subscriber_task = None


@router.websocket("/ws/chats/{chat_id}")
async def chat_ws(
    websocket: WebSocket,
    chat_id: int,
) -> None:
    async with AsyncSessionLocal() as session:
        try:
            cabinet_session = await resolve_cabinet_session_from_websocket(websocket, session)
        except HTTPException as exc:
            await websocket.close(code=1008, reason=str(exc.detail))
            return

        chat_exists_result = await session.execute(
            select(Chat.id).where(Chat.id == chat_id, Chat.user_id == cabinet_session.user_id)
        )
        if chat_exists_result.scalar_one_or_none() is None:
            await websocket.close(code=1008, reason="Chat not found")
            return

    await manager.connect(chat_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(chat_id, websocket)
