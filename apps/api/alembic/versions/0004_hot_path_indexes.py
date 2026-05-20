"""hot-path composite indexes

Revision ID: 0004_hot_path_indexes
Revises: 0003_cabinet_identity_and_files
Create Date: 2026-05-19
"""

from alembic import op

revision = "0004_hot_path_indexes"
down_revision = "0003_cabinet_identity_and_files"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_agent_runs_status_lease_expires_at "
        "ON agent_runs(status, lease_expires_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_messages_chat_id_created_at "
        "ON messages(chat_id, created_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_messages_chat_id_created_at")
    op.execute("DROP INDEX IF EXISTS ix_agent_runs_status_lease_expires_at")
