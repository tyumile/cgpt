from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "cgpt-api"
    app_role: str = Field(default="api", alias="APP_ROLE")
    database_url: str = Field(
        default="postgresql+asyncpg://cgpt:cgpt@localhost:5432/cgpt",
        alias="DATABASE_URL",
    )
    workspace_root: Path = Field(default=Path("/workspace/runtime/workspaces/default"), alias="WORKSPACE_ROOT")
    codex_timeout_seconds: int = Field(default=600, alias="CODEX_TIMEOUT_SECONDS")
    codex_binary: str = Field(default="codex", alias="CODEX_BINARY")
    codex_config_dir: Path | None = Field(default=None, alias="CODEX_CONFIG_DIR")
    codex_sandbox_mode: str = Field(default="workspace-write", alias="CODEX_SANDBOX_MODE")

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    run_queue_name: str = Field(default="agent_runs:queue", alias="RUN_QUEUE_NAME")
    run_processing_queue_name: str = Field(default="agent_runs:processing", alias="RUN_PROCESSING_QUEUE_NAME")
    run_events_channel: str = Field(default="agent_runs:events", alias="RUN_EVENTS_CHANNEL")
    run_max_retries: int = Field(default=1, alias="RUN_MAX_RETRIES")
    run_lease_seconds: int = Field(default=90, alias="RUN_LEASE_SECONDS")
    run_heartbeat_seconds: int = Field(default=10, alias="RUN_HEARTBEAT_SECONDS")
    run_reaper_interval_seconds: int = Field(default=15, alias="RUN_REAPER_INTERVAL_SECONDS")
    run_queue_block_seconds: int = Field(default=5, alias="RUN_QUEUE_BLOCK_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
