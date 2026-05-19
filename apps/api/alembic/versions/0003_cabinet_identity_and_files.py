"""cabinet identity and uploaded files

Revision ID: 0003_cabinet_identity_and_files
Revises: 0002_queue_worker_fields
Create Date: 2026-05-18
"""

from alembic import op

revision = "0003_cabinet_identity_and_files"
down_revision = "0002_queue_worker_fields"
branch_labels = None
depends_on = None


LEGACY_EMAIL = "legacy@local"


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS cabinet_users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(320) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS cabinet_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES cabinet_users(id) ON DELETE CASCADE,
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_cabinet_sessions_user_id ON cabinet_sessions(user_id)")

    op.execute("ALTER TABLE chats ADD COLUMN IF NOT EXISTS user_id INTEGER")
    op.execute(
        f"""
        INSERT INTO cabinet_users (email, full_name)
        VALUES ('{LEGACY_EMAIL}', 'Legacy User')
        ON CONFLICT (email) DO NOTHING
        """
    )
    op.execute(
        f"""
        UPDATE chats
        SET user_id = (SELECT id FROM cabinet_users WHERE email = '{LEGACY_EMAIL}')
        WHERE user_id IS NULL
        """
    )
    op.execute("ALTER TABLE chats ALTER COLUMN user_id SET NOT NULL")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'fk_chats_user_id_cabinet_users'
            ) THEN
                ALTER TABLE chats
                ADD CONSTRAINT fk_chats_user_id_cabinet_users
                FOREIGN KEY (user_id)
                REFERENCES cabinet_users(id)
                ON DELETE RESTRICT;
            END IF;
        END
        $$;
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_chats_user_id ON chats(user_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES cabinet_users(id) ON DELETE RESTRICT,
            chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE RESTRICT,
            message_id INTEGER NULL REFERENCES messages(id) ON DELETE SET NULL,
            original_name VARCHAR(512) NOT NULL,
            stored_name VARCHAR(512) NOT NULL,
            relative_path VARCHAR(2048) NOT NULL,
            mime_type VARCHAR(255) NOT NULL,
            size_bytes INTEGER NOT NULL,
            preview_text TEXT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_uploaded_files_chat_id ON uploaded_files(chat_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_uploaded_files_message_id ON uploaded_files(message_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_uploaded_files_user_id ON uploaded_files(user_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS uploaded_files")

    op.execute("DROP INDEX IF EXISTS ix_chats_user_id")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'fk_chats_user_id_cabinet_users'
            ) THEN
                ALTER TABLE chats DROP CONSTRAINT fk_chats_user_id_cabinet_users;
            END IF;
        END
        $$;
        """
    )
    op.execute("ALTER TABLE chats DROP COLUMN IF EXISTS user_id")

    op.execute("DROP INDEX IF EXISTS ix_cabinet_sessions_user_id")
    op.execute("DROP TABLE IF EXISTS cabinet_sessions")
    op.execute("DROP TABLE IF EXISTS cabinet_users")
