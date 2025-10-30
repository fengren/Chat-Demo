from typing import Optional
from fastapi import Header


async def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    """占位：解析 Supabase JWT，返回 user_id。无则游客返回 None。"""
    # TODO: 使用 SUPABASE_JWKS_URL 校验并解析
    if not authorization:
        return None
    return None


