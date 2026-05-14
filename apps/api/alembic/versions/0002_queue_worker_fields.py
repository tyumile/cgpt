"""queue worker fields

Revision ID: 0002_queue_worker_fields
Revises: 0001_stage1_schema
Create Date: 2026-05-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_queue_worker_fields"
down_revision = "0001_stage1_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS queue_job_id VARCHAR(128)")
    op.execute("ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS attempt INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS heartbeat_at TIMESTAMPTZ")
    op.execute("ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS lease_expires_at TIMESTAMPTZ")
    op.execute("ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS deadletter_reason TEXT")
    op.create_index("ix_agent_runs_queue_job_id", "agent_runs", ["queue_job_id"], if_not_exists=True)


def downgrade() -> None:
    op.drop_index("ix_agent_runs_queue_job_id", table_name="agent_runs")
    op.drop_column("agent_runs", "deadletter_reason")
    op.drop_column("agent_runs", "lease_expires_at")
    op.drop_column("agent_runs", "heartbeat_at")
    op.drop_column("agent_runs", "attempt")
    op.drop_column("agent_runs", "queue_job_id")
