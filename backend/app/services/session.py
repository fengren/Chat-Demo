from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.automap import automap_base
import uuid
from ..config import settings


# 创建数据库连接
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = automap_base()
Base.prepare(autoload_with=engine)

# 获取表模型
ChatSessions = Base.classes.chat_sessions
ChatMessages = Base.classes.chat_messages


def create_session(title: str = None, user_id: str = None) -> dict:
    """创建新会话"""
    with SessionLocal() as db_session:
        session_id = str(uuid.uuid4())
        session_obj = ChatSessions(
            id=session_id,
            user_id=user_id,
            title=title or "新对话",
            created_at=datetime.now()
        )
        db_session.add(session_obj)
        db_session.commit()
        db_session.refresh(session_obj)
        return {
            "id": str(session_obj.id),
            "title": session_obj.title,
            "user_id": str(session_obj.user_id) if session_obj.user_id else None,
            "created_at": session_obj.created_at.isoformat() if session_obj.created_at else None
        }


def get_session(session_id: str) -> dict:
    """获取会话信息"""
    with SessionLocal() as db_session:
        stmt = select(ChatSessions).where(ChatSessions.id == session_id)
        session_obj = db_session.scalar(stmt)
        if not session_obj:
            return None
        return {
            "id": str(session_obj.id),
            "title": session_obj.title,
            "user_id": str(session_obj.user_id) if session_obj.user_id else None,
            "created_at": session_obj.created_at.isoformat() if session_obj.created_at else None
        }


def list_sessions(user_id: str = None, limit: int = 50) -> list:
    """列出所有会话"""
    with SessionLocal() as db_session:
        stmt = select(ChatSessions)
        if user_id:
            stmt = stmt.where(ChatSessions.user_id == user_id)
        stmt = stmt.order_by(ChatSessions.created_at.desc()).limit(limit)
        sessions = db_session.scalars(stmt).all()
        return [
            {
                "id": str(s.id),
                "title": s.title,
                "user_id": str(s.user_id) if s.user_id else None,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in sessions
        ]


def update_session_title(session_id: str, title: str) -> dict:
    """更新会话标题"""
    with SessionLocal() as db_session:
        stmt = select(ChatSessions).where(ChatSessions.id == session_id)
        session_obj = db_session.scalar(stmt)
        if not session_obj:
            raise ValueError(f"Session {session_id} not found")
        session_obj.title = title
        db_session.commit()
        db_session.refresh(session_obj)
        return {
            "id": str(session_obj.id),
            "title": session_obj.title,
            "user_id": str(session_obj.user_id) if session_obj.user_id else None,
            "created_at": session_obj.created_at.isoformat() if session_obj.created_at else None
        }


def get_session_messages(session_id: str) -> list:
    """获取会话消息历史"""
    with SessionLocal() as db_session:
        stmt = select(ChatMessages).where(ChatMessages.session_id == session_id).order_by(ChatMessages.created_at)
        messages = db_session.scalars(stmt).all()
        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "metadata": m.metadata if hasattr(m, 'metadata') and m.metadata else None,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in messages
        ]


def delete_session(session_id: str) -> bool:
    """删除会话及其所有消息"""
    from ..services.message import delete_messages_by_session
    
    with SessionLocal() as db_session:
        # 先删除所有消息
        delete_messages_by_session(session_id)
        
        # 然后删除会话
        stmt = select(ChatSessions).where(ChatSessions.id == session_id)
        session_obj = db_session.scalar(stmt)
        if not session_obj:
            return False
        
        db_session.delete(session_obj)
        db_session.commit()
        return True

