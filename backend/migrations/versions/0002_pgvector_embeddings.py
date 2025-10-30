from alembic import op, context
import sqlalchemy as sa


revision = "0002_pgvector_embeddings"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dialect = context.get_context().dialect.name
    if dialect == "postgresql":
        # 暂不创建 pgvector 扩展（需要数据库先安装）
        # op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        # 使用普通 ARRAY 代替，后续可迁移到 pgvector 类型
        id_col = sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()"))
        ts_col = sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"))
        emb_col = sa.dialects.postgresql.ARRAY(sa.Float())
    else:
        # 非 Postgres：创建兼容表结构，embedding 存为 TEXT（JSON 序列化向量）
        id_col = sa.Column("id", sa.Text(), primary_key=True)
        ts_col = sa.Column("created_at", sa.DateTime(), nullable=True)
        emb_col = sa.Text()

    op.create_table(
        "embeddings",
        id_col,
        sa.Column("doc_id", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", emb_col, nullable=False),
        ts_col,
    )


def downgrade() -> None:
    op.drop_table("embeddings")

