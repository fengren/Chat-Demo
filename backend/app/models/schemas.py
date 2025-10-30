from pydantic import BaseModel, Field
from typing import Any, Optional, List


class Message(BaseModel):
    role: str
    content: str
    metadata: Optional[dict[str, Any]] = None


class ChatTurn(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    messages: List[Message]


class IntentResult(BaseModel):
    intent: str
    confidence: float = Field(ge=0, le=1)
    reason: Optional[str] = None


