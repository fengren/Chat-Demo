import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

# 尝试从项目根目录与 backend 目录加载 .env
_CONFIG_FILE_PATH = Path(__file__).resolve()
_PROJECT_ROOT = _CONFIG_FILE_PATH.parents[2]
_BACKEND_ROOT = _CONFIG_FILE_PATH.parents[1]
load_dotenv(_PROJECT_ROOT / ".env")
load_dotenv(_BACKEND_ROOT / ".env")


class Settings(BaseModel):
    # Server
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")

    # LLM (OpenAI-compatible)
    LLM_API_BASE: str = os.getenv("LLM_API_BASE", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL_CHAT: str = os.getenv("LLM_MODEL_CHAT", "gpt-4o-mini")
    LLM_MODEL_MODERATION: str = os.getenv("LLM_MODEL_MODERATION", "")
    
    # 向量大模型配置 (用于嵌入向量生成)
    EMBEDDING_API_BASE: str = os.getenv("EMBEDDING_API_BASE", "")
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "1536"))

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_JWKS_URL: str = os.getenv("SUPABASE_JWKS_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # Database / Alembic
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # RAG
    RAG_BACKEND: str = os.getenv("RAG_BACKEND", "supabase_pgvector")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_data")
    INDEX_NAME: str = os.getenv("INDEX_NAME", "documents")
    RAG_ENDPOINT: str = os.getenv("RAG_ENDPOINT", "")
    RAG_API_KEY: str = os.getenv("RAG_API_KEY", "")

    # Langfuse
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "")
    LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "ai-chat-backend")
    PROM_ENABLED: bool = os.getenv("PROM_ENABLED", "true").lower() == "true"
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # Langflow
    LANGFLOW_BASE_URL: str = os.getenv("LANGFLOW_BASE_URL", "")
    LANGFLOW_API_KEY: str = os.getenv("LANGFLOW_API_KEY", "")

    # Mem0
    MEM0_API_KEY: str = os.getenv("MEM0_API_KEY", "")
    MEM0_BASE_URL: str = os.getenv("MEM0_BASE_URL", "")


settings = Settings()


