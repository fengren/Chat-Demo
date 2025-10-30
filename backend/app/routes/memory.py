from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.memory import memory_manager
from typing import List, Dict, Any, Optional


router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryResponse(BaseModel):
    id: str
    memory: str
    type: Optional[str] = None
    importance: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/{session_id}")
async def get_memories(session_id: str, limit: int = 50) -> Dict[str, Any]:
    """获取指定会话的所有记忆"""
    try:
        user_id = memory_manager.get_user_id(session_id)
        
        if not memory_manager.memory:
            return {"memories": [], "count": 0}
        
        # 获取所有记忆
        all_memories = await memory_manager.get_all_memories(user_id=user_id, limit=limit)
        
        if not all_memories:
            return {"memories": [], "count": 0}
        
        # 格式化记忆数据
        formatted_memories = []
        for mem in all_memories:
            # 处理不同的返回格式
            if isinstance(mem, dict):
                formatted_memories.append({
                    "id": mem.get("id", ""),
                    "memory": mem.get("memory", ""),
                    "type": mem.get("metadata", {}).get("type", "unknown") if isinstance(mem.get("metadata"), dict) else "unknown",
                    "importance": mem.get("metadata", {}).get("importance", "medium") if isinstance(mem.get("metadata"), dict) else "medium",
                    "metadata": mem.get("metadata", {}),
                    "created_at": mem.get("created_at"),
                })
            else:
                # 如果是字符串格式
                formatted_memories.append({
                    "id": "",
                    "memory": str(mem),
                    "type": "unknown",
                    "importance": "medium",
                    "metadata": {},
                    "created_at": None,
                })
        
        return {
            "memories": formatted_memories,
            "count": len(formatted_memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memories: {str(e)}")


@router.get("/{session_id}/search")
async def search_memories(session_id: str, q: str, limit: int = 10) -> Dict[str, Any]:
    """搜索相关记忆"""
    try:
        user_id = memory_manager.get_user_id(session_id)
        
        if not memory_manager.memory:
            return {"memories": [], "count": 0}
        
        # 搜索记忆
        memories = memory_manager.memory.search(query=q, user_id=user_id, limit=limit)
        
        if not memories or "memories" not in memories:
            return {"memories": [], "count": 0}
        
        # 格式化记忆数据
        formatted_memories = []
        for mem in memories["memories"]:
            formatted_memories.append({
                "id": mem.get("id", ""),
                "memory": mem.get("memory", ""),
                "type": mem.get("metadata", {}).get("type", "unknown"),
                "importance": mem.get("metadata", {}).get("importance", "medium"),
                "metadata": mem.get("metadata", {}),
                "created_at": mem.get("created_at"),
                "score": mem.get("score"),  # 相关性分数
            })
        
        return {
            "memories": formatted_memories,
            "count": len(formatted_memories),
            "query": q
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {str(e)}")


@router.delete("/{session_id}/{memory_id}")
async def delete_memory(session_id: str, memory_id: str) -> Dict[str, Any]:
    """删除指定记忆"""
    try:
        if not memory_manager.memory:
            raise HTTPException(status_code=400, detail="Memory manager not initialized")
        
        result = memory_manager.memory.delete(memory_id=memory_id)
        return {"success": True, "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")

