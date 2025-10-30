from datetime import datetime
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import uuid
from ..config import settings


# 创建数据库连接
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = automap_base()
Base.prepare(autoload_with=engine)

# 获取表模型
ChatMessages = Base.classes.chat_messages


def save_message(session_id: str, role: str, content: str, user_id: str = None, metadata: dict = None) -> dict:
    """保存消息"""
    with SessionLocal() as db_session:
        message = ChatMessages(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            metadata=metadata or {},
            created_at=datetime.now()
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        return {
            "id": str(message.id),
            "session_id": str(message.session_id),
            "role": message.role,
            "content": message.content,
            "metadata": message.metadata if hasattr(message, 'metadata') and message.metadata else None,
            "created_at": message.created_at.isoformat() if message.created_at else None
        }


def count_messages_by_session(session_id: str) -> int:
    """统计会话的消息数量"""
    with SessionLocal() as db_session:
        stmt = select(func.count(ChatMessages.id)).where(ChatMessages.session_id == session_id)
        count = db_session.scalar(stmt)
        return count if count else 0


def delete_messages_by_session(session_id: str) -> int:
    """删除会话的所有消息，返回删除的数量"""
    with SessionLocal() as db_session:
        stmt = select(ChatMessages).where(ChatMessages.session_id == session_id)
        messages = db_session.scalars(stmt).all()
        count = len(messages)
        for msg in messages:
            db_session.delete(msg)
        db_session.commit()
        return count


def get_messages_by_session(session_id: str, limit: int = 100) -> list:
    """获取会话的所有消息"""
    with SessionLocal() as db_session:
        stmt = select(ChatMessages).where(ChatMessages.session_id == session_id).order_by(ChatMessages.created_at).limit(limit)
        messages = db_session.scalars(stmt).all()
        return [
            {
                "id": str(m.id),
                "session_id": str(m.session_id),
                "role": m.role,
                "content": m.content,
                "metadata": m.metadata if hasattr(m, 'metadata') and m.metadata else None,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in messages
        ]

