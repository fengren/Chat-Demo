from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.session import (
    create_session as create_session_service,
    get_session as get_session_service,
    list_sessions as list_sessions_service,
    update_session_title as update_session_title_service,
    get_session_messages as get_session_messages_service,
    delete_session as delete_session_service
)
from ..services.message import get_messages_by_session


router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    title: str = None


class UpdateTitleRequest(BaseModel):
    title: str


@router.post("")
async def create_session(body: CreateSessionRequest) -> dict:
    """创建新会话"""
    try:
        session = create_session_service(title=body.title)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_sessions_endpoint() -> list:
    """列出所有会话"""
    try:
        sessions = list_sessions_service()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session_endpoint(session_id: str) -> dict:
    """获取会话详情"""
    try:
        session = get_session_service(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}/title")
async def update_title(session_id: str, body: UpdateTitleRequest) -> dict:
    """更新会话标题"""
    try:
        session = update_session_title_service(session_id, body.title)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/messages")
async def get_session_messages_endpoint(session_id: str) -> list:
    """获取会话消息历史"""
    try:
        messages = get_session_messages_service(session_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session_endpoint(session_id: str) -> dict:
    """删除会话"""
    try:
        deleted = delete_session_service(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
