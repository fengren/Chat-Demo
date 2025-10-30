from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncGenerator
import asyncio
import logging

from .config import settings
from .routes.session import router as session_router
from .routes.chat import router as chat_router
from .routes.memory import router as memory_router
from .logging_config import setup_logging


def create_app() -> FastAPI:
    # 初始化日志
    setup_logging(level="INFO")
    logger = logging.getLogger(__name__)
    
    app = FastAPI(title="AI Chat Demo", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    app.include_router(session_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(memory_router, prefix="/api")

    return app


app = create_app()


