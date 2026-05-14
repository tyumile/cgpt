import asyncio
import logging

from sqlalchemy import select

from app.config.main import get_settings
from app.db.main import AsyncSessionLocal
from app.db.models import AgentRun
from app.modules.agent_runs.main import heartbeat_run, mark_run_running
from app.modules.assistant_finalize.main import finalize_failure, finalize_success
from app.modules.codex_runner.main import CodexRunError, run_codex_stream
from app.modules.messages_store.main import get_last_messages
from app.modules.prompt_builder.main import build_prompt
from app.modules.realtime.main import publish_event
from app.modules.workspaces.main import get_current_workspace

logger = logging.getLogger(__name__)


async def process_agent_run(*, run_id: int, chat_id: int) -> None:
    settings = get_settings()

    async with AsyncSessionLocal() as session:
        run_result = await session.execute(select(AgentRun).where(AgentRun.id == run_id))
        run = run_result.scalar_one_or_none()
        if run is None:
            logger.error("Agent run not found: %s", run_id)
            return

        await mark_run_running(session, run)
        await publish_event(chat_id, {"event": "agent_run_started", "agent_run_id": run.id})

        workspace = await get_current_workspace(session)
        context_messages = await get_last_messages(session, chat_id=chat_id, limit=30)
        prompt = build_prompt(messages=context_messages, workspace_path=workspace.root_path)

        streamed_parts: list[str] = []
        last_heartbeat = asyncio.get_event_loop().time()

        async def on_chunk(chunk: str) -> None:
            nonlocal last_heartbeat
            streamed_parts.append(chunk)
            await publish_event(
                chat_id,
                {
                    "event": "assistant_chunk",
                    "agent_run_id": run.id,
                    "chunk": chunk,
                    "full_text": "".join(streamed_parts),
                },
            )

            now = asyncio.get_event_loop().time()
            if now - last_heartbeat >= settings.run_heartbeat_seconds:
                await heartbeat_run(session, run, lease_seconds=settings.run_lease_seconds)
                last_heartbeat = now

        try:
            final_text = await run_codex_stream(
                run_id=run.id,
                prompt=prompt,
                workspace_path=workspace.root_path,
                on_chunk=on_chunk,
            )
            output_message_id = await finalize_success(
                session,
                run=run,
                workspace_id=workspace.id,
                chat_id=chat_id,
                content=final_text,
            )
            await publish_event(
                chat_id,
                {
                    "event": "assistant_done",
                    "agent_run_id": run.id,
                    "output_message_id": output_message_id,
                    "full_text": final_text,
                },
            )
        except CodexRunError as exc:
            error_text = str(exc)
            await finalize_failure(session, run=run, error=error_text)
            await publish_event(
                chat_id,
                {
                    "event": "assistant_error",
                    "agent_run_id": run.id,
                    "error": error_text,
                },
            )
            raise
        except Exception as exc:  # pragma: no cover
            logger.exception("Unexpected agent execution error")
            error_text = f"Unexpected error: {exc}"
            await finalize_failure(session, run=run, error=error_text)
            await publish_event(
                chat_id,
                {
                    "event": "assistant_error",
                    "agent_run_id": run.id,
                    "error": error_text,
                },
            )
            raise
