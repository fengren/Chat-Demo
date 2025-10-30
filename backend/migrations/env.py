from __future__ import with_statement
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
# __file__ = backend/migrations/env.py
# parents[0] = backend/migrations/
# parents[1] = backend/
# parents[2] = 项目根目录
_project_root = Path(__file__).resolve().parents[2]
_backend_root = Path(__file__).resolve().parents[1]
# 尝试从项目根目录和 backend 目录加载 .env
env_loaded = load_dotenv(_project_root / ".env")
env_loaded_backend = load_dotenv(_backend_root / ".env")
print(f"Loading .env from: {_project_root / '.env'}, loaded: {env_loaded}")
print(f"Loading .env from: {_backend_root / '.env'}, loaded: {env_loaded_backend}")


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    print(url)
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # 优先使用环境变量 DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    print("database_url", database_url)
    if database_url:
        from sqlalchemy import create_engine
        connectable = create_engine(database_url, poolclass=pool.NullPool)
    else:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


