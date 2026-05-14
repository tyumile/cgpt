from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.main import get_settings
from app.db.models import Workspace


async def ensure_default_workspace(session: AsyncSession) -> Workspace:
    settings = get_settings()
    workspace_root = Path(settings.workspace_root)
    workspace_root.mkdir(parents=True, exist_ok=True)

    result = await session.execute(select(Workspace).where(Workspace.slug == "default"))
    workspace = result.scalar_one_or_none()
    if workspace is not None:
        return workspace

    workspace = Workspace(
        slug="default",
        name="Default Workspace",
        root_path=str(workspace_root),
    )
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)
    return workspace


async def get_current_workspace(session: AsyncSession) -> Workspace:
    return await ensure_default_workspace(session)
