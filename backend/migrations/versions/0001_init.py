from alembic import op
import sqlalchemy as sa
from alembic import context


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    dialect = context.get_context().dialect.name

    if dialect == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        id_col = sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()"))
        user_col = sa.Column("user_id", sa.UUID(), nullable=True)
        sess_fk_col = sa.Column("session_id", sa.UUID(), nullable=False)
        ts_col = sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"))
        json_col = sa.JSON()
    else:
        # SQLite 等：使用 TEXT 主键与无时区时间戳；不创建扩展
        id_col = sa.Column("id", sa.Text(), primary_key=True)
        user_col = sa.Column("user_id", sa.Text(), nullable=True)
        sess_fk_col = sa.Column("session_id", sa.Text(), nullable=False)
        ts_col = sa.Column("created_at", sa.DateTime(), nullable=True)
        json_col = sa.Text()

    op.create_table(
        "chat_sessions",
        id_col,
        user_col,
        sa.Column("title", sa.Text(), nullable=True),
        ts_col,
    )

    op.create_table(
        "chat_messages",
        id_col.copy(),
        sess_fk_col,
        user_col.copy(),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", json_col, nullable=True),
        ts_col.copy(),
    )

    # SQLite 会允许创建这些组合索引；如有需要可在应用层兼容
    op.create_index("ix_sessions_user_created", "chat_sessions", ["user_id", "created_at"])
    op.create_index("ix_messages_session_created", "chat_messages", ["session_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_messages_session_created", table_name="chat_messages")
    op.drop_index("ix_sessions_user_created", table_name="chat_sessions")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")


