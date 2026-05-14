import asyncio
import logging
import os
import shutil
from pathlib import Path

from app.config.main import get_settings

logger = logging.getLogger(__name__)


class CodexRunError(Exception):
    pass


async def run_codex_stream(
    *,
    run_id: int,
    prompt: str,
    workspace_path: str,
    on_chunk,
) -> str:
    settings = get_settings()

    if shutil.which(settings.codex_binary) is None:
        raise CodexRunError("Codex CLI is not installed. Please install and authenticate Codex CLI.")

    workspace = Path(workspace_path).resolve()
    allowed = Path(settings.workspace_root).resolve()
    if workspace != allowed:
        raise CodexRunError("Workspace path is invalid for Stage 1 runner.")

    output_file = workspace / f".codex_last_message_{run_id}.txt"
    if output_file.exists():
        output_file.unlink()

    cmd = [
        settings.codex_binary,
        "exec",
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "--cd",
        str(workspace),
        "--output-last-message",
        str(output_file),
        "-",
    ]

    env = os.environ.copy()
    if settings.codex_config_dir is not None:
        env["CODEX_HOME"] = str(settings.codex_config_dir)

    logger.info("Launching codex exec command in workspace", extra={"workspace": str(workspace), "run_id": run_id})

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(workspace),
        env=env,
    )

    stderr_chunks: list[str] = []

    async def consume_stdout() -> None:
        assert process.stdout is not None
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="ignore")
            await on_chunk(text)

    async def consume_stderr() -> None:
        assert process.stderr is not None
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="ignore")
            stderr_chunks.append(text)
            logger.warning("codex stderr: %s", text.rstrip())

    assert process.stdin is not None
    process.stdin.write(prompt.encode("utf-8"))
    await process.stdin.drain()
    process.stdin.close()

    try:
        await asyncio.wait_for(asyncio.gather(consume_stdout(), consume_stderr()), timeout=settings.codex_timeout_seconds)
    except asyncio.TimeoutError as exc:
        process.kill()
        await process.wait()
        raise CodexRunError("Codex execution timed out.") from exc

    return_code = await process.wait()

    final_text = ""
    if output_file.exists():
        final_text = output_file.read_text(encoding="utf-8").strip()

    if return_code != 0:
        stderr_text = "".join(stderr_chunks).strip()
        if "auth" in stderr_text.lower() or "login" in stderr_text.lower():
            raise CodexRunError("Codex CLI is not authenticated. Please login on host and restart.")
        raise CodexRunError(stderr_text or "Codex execution failed.")

    if not final_text:
        final_text = "".join(stderr_chunks).strip() or "Codex returned an empty response."

    return final_text
