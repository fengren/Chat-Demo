from typing import List, Dict, Any, Optional
from mem0 import Memory
from ..config import settings
import logging
import json
import os

logger = logging.getLogger(__name__)


class MemoryManager:
    """记忆管理器，使用 mem0 管理用户记忆"""
    
    def __init__(self):
        self.memory: Optional[Memory] = None
        self._initialize_memory()
    
    def _initialize_memory(self):
        """初始化 mem0"""
        logger.info("Initializing Mem0 memory manager...")
        logger.debug(f"LLM_API_KEY configured: {bool(settings.LLM_API_KEY)}")
        logger.debug(f"LLM_API_BASE: {settings.LLM_API_BASE}")
        logger.debug(f"LLM_MODEL_CHAT: {settings.LLM_MODEL_CHAT}")
        logger.debug(f"EMBEDDING_API_BASE: {settings.EMBEDDING_API_BASE}")
        logger.debug(f"EMBEDDING_API_KEY configured: {bool(settings.EMBEDDING_API_KEY)}")
        logger.debug(f"EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
        logger.debug(f"MEM0_API_KEY configured: {bool(settings.MEM0_API_KEY)}")
        logger.debug(f"MEM0_BASE_URL: {settings.MEM0_BASE_URL}")
        
        # 设置 API Key - 优先使用向量大模型的配置
        if settings.EMBEDDING_API_KEY:
            os.environ["OPENAI_API_KEY"] = settings.EMBEDDING_API_KEY
            logger.info("Set OPENAI_API_KEY from EMBEDDING_API_KEY for Mem0 compatibility")
        elif settings.LLM_API_KEY and not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = settings.LLM_API_KEY
            logger.info("Set OPENAI_API_KEY from LLM_API_KEY for Mem0 compatibility")
        
        # 设置 API Base URL - 优先使用向量大模型的配置
        if settings.EMBEDDING_API_BASE:
            os.environ["OPENAI_BASE_URL"] = settings.EMBEDDING_API_BASE
            logger.info(f"Set OPENAI_BASE_URL to {settings.EMBEDDING_API_BASE} for Mem0 compatibility")
        elif settings.LLM_API_BASE and settings.LLM_API_BASE != "https://api.openai.com/v1":
            os.environ["OPENAI_BASE_URL"] = settings.LLM_API_BASE
            logger.info(f"Set OPENAI_BASE_URL to {settings.LLM_API_BASE} for Mem0 compatibility")
        
        # 设置嵌入模型
        if settings.EMBEDDING_MODEL:
            os.environ["OPENAI_EMBEDDING_MODEL"] = settings.EMBEDDING_MODEL
            logger.info(f"Set OPENAI_EMBEDDING_MODEL to {settings.EMBEDDING_MODEL}")
        else:
            # 如果没有配置嵌入模型，使用默认值
            os.environ["OPENAI_EMBEDDING_MODEL"] = "text-embedding-3-small"
            logger.info("Using default text-embedding-3-small as embedding model")
        
        # 打印最终配置信息
        logger.info(f"=== Mem0 配置信息 ===")
        logger.info(f"API Base URL: {os.getenv('OPENAI_BASE_URL', 'Not set')}")
        logger.info(f"API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
        logger.info(f"Embedding Model: {os.getenv('OPENAI_EMBEDDING_MODEL', 'Not set')}")
        logger.info(f"Chat Model: {settings.LLM_MODEL_CHAT}")
        logger.info(f"========================")
        
        try:
            # 使用简化的配置，让 Mem0 使用默认设置
            if settings.MEM0_API_KEY:
                # 使用 Mem0 API 模式
                logger.info("Using Mem0 API mode")
                config = {
                    "api_key": settings.MEM0_API_KEY
                }
                if settings.MEM0_BASE_URL:
                    config["api_url"] = settings.MEM0_BASE_URL
                self.memory = Memory.from_config(config)
            else:
                # 使用本地模式，依赖环境变量
                logger.info("Using Mem0 local mode with environment variables")
                # 确保 OPENAI_API_KEY 已设置
                if not os.getenv("OPENAI_API_KEY"):
                    logger.warning("OPENAI_API_KEY not set, Mem0 may not work properly")
                # 使用最简单的配置，让 Mem0 从环境变量读取配置
                self.memory = Memory()
            
            # 手动设置嵌入模型（因为 Mem0 不支持通过配置传递）
            if hasattr(self.memory, 'embedding_model') and self.memory.embedding_model:
                # 修改嵌入模型的模型名称
                if hasattr(self.memory.embedding_model, 'model'):
                    old_model = self.memory.embedding_model.model
                    self.memory.embedding_model.model = settings.EMBEDDING_MODEL
                    logger.info(f"Updated embedding model from {old_model} to {settings.EMBEDDING_MODEL}")
                
                # 修改嵌入模型的维度
                if hasattr(self.memory.embedding_model, 'dims'):
                    old_dims = self.memory.embedding_model.dims
                    self.memory.embedding_model.dims = settings.EMBEDDING_DIM
                    logger.info(f"Updated embedding dims from {old_dims} to {settings.EMBEDDING_DIM}")
                
                # 重新创建向量存储集合以使用正确的维度
                if hasattr(self.memory, 'vector_store') and self.memory.vector_store:
                    try:
                        # 删除现有集合
                        if hasattr(self.memory.vector_store, 'delete_col'):
                            self.memory.vector_store.delete_col(self.memory.collection_name)
                            logger.info(f"Deleted existing collection {self.memory.collection_name}")
                        
                        # 重新创建集合
                        self.memory.vector_store.create_col(
                            name=self.memory.collection_name, 
                            vector_size=self.memory.embedding_model.dims
                        )
                        logger.info(f"Recreated collection {self.memory.collection_name} with vector size {self.memory.embedding_model.dims}")
                    except Exception as e:
                        logger.warning(f"Failed to recreate collection: {e}")
            
            # 手动设置 LLM 模型（因为 Mem0 不支持通过配置传递）
            if hasattr(self.memory, 'llm') and self.memory.llm:
                # 修改 LLM 的模型名称
                if hasattr(self.memory.llm, 'config') and hasattr(self.memory.llm.config, 'model'):
                    old_model = self.memory.llm.config.model
                    self.memory.llm.config.model = settings.LLM_MODEL_CHAT
                    logger.info(f"Updated LLM model from {old_model} to {settings.LLM_MODEL_CHAT}")
                elif hasattr(self.memory.llm, 'model'):
                    old_model = self.memory.llm.model
                    self.memory.llm.model = settings.LLM_MODEL_CHAT
                    logger.info(f"Updated LLM model from {old_model} to {settings.LLM_MODEL_CHAT}")
            
            logger.info("✓ Mem0 initialized successfully")
            logger.debug(f"Memory instance type: {type(self.memory)}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Mem0: {e}", exc_info=True)
            self.memory = None
    
    def get_user_id(self, session_id: str) -> str:
        """根据 session_id 生成 user_id（可以后续扩展为实际的用户ID）"""
        # 目前使用 session_id 作为 user_id，后续可以关联真实用户
        return f"session_{session_id}"
    
    async def extract_key_memories(self, user_input: str, assistant_reply: str) -> List[Dict[str, Any]]:
        """使用 LLM 提取关键记忆信息"""
        if not self.memory or not settings.LLM_API_KEY:
            logger.warning("Memory or LLM_API_KEY not available, skipping memory extraction")
            return []
        
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            # 初始化 LLM 用于提取
            llm_kwargs = {
                "model": settings.LLM_MODEL_CHAT,
                "temperature": 0.3,  # 降低温度以获得更稳定的提取
            }
            if settings.LLM_API_BASE:
                llm_kwargs["base_url"] = settings.LLM_API_BASE
            if settings.LLM_API_KEY:
                llm_kwargs["api_key"] = settings.LLM_API_KEY
            
            extract_llm = ChatOpenAI(**llm_kwargs)
            
            prompt = f"""请分析以下对话，提取值得记忆的关键信息。只提取以下类型的信息：
1. 用户偏好（喜欢的、不喜欢的）
2. 个人事实（姓名、职业、位置、兴趣等）
3. 重要任务或目标
4. 重要的事件或约定

如果对话中没有值得记忆的信息（如简单问答、日常寒暄），返回空数组。

对话：
用户: {user_input}
助手: {assistant_reply}

请以 JSON 格式返回，格式如下：
[
  {{
    "type": "preference" | "fact" | "task" | "event",
    "content": "简洁的关键信息描述",
    "importance": "high" | "medium" | "low"
  }}
]

只返回 JSON 数组，不要其他文字："""
            
            logger.info(f"Extracting memories from conversation: user_input={user_input[:50]}...")
            messages = [HumanMessage(content=prompt)]
            response = await extract_llm.ainvoke(messages)
            
            logger.info(f"Memory extraction response: {response.content[:200]}...")
            
            # 解析 JSON 响应
            try:
                content = response.content.strip()
                # 移除可能的 markdown 代码块标记
                if content.startswith("```"):
                    parts = content.split("```")
                    if len(parts) > 1:
                        content = parts[1]
                        if content.startswith("json"):
                            content = content[4:]
                content = content.strip()
                
                memories = json.loads(content)
                if isinstance(memories, list):
                    # 过滤掉低重要性的记忆
                    filtered = [m for m in memories if m.get("importance") != "low"]
                    logger.info(f"Extracted {len(filtered)} memories (filtered from {len(memories)})")
                    return filtered
                logger.warning(f"Extracted memories is not a list: {type(memories)}")
                return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse memory extraction JSON: {e}")
                logger.error(f"Response content: {response.content}")
                # 尝试直接提取关键信息作为fallback
                if "喜欢" in user_input or "不喜欢" in user_input or "偏好" in user_input.lower():
                    logger.info("Fallback: extracting preference from user input")
                    return [{
                        "type": "preference",
                        "content": user_input,
                        "importance": "medium"
                    }]
                return []
        except Exception as e:
            # 打印当前配置信息用于调试
            logger.error(f"=== 记忆提取失败时的配置信息 ===")
            logger.error(f"API Base URL: {os.getenv('OPENAI_BASE_URL', 'Not set')}")
            logger.error(f"API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
            logger.error(f"Embedding Model: {os.getenv('OPENAI_EMBEDDING_MODEL', 'Not set')}")
            logger.error(f"Chat Model: {settings.LLM_MODEL_CHAT}")
            logger.error(f"Conversation: {conversation[:100]}...")
            logger.error(f"User ID: {user_id}")
            logger.error(f"=====================================")
            
            # 如果是连接错误或认证错误，记录警告但不抛出异常
            if "Connection error" in str(e) or "Invalid token" in str(e) or "API" in str(e):
                logger.warning(f"Memory extraction failed due to API issues, skipping: {e}")
            else:
                logger.error(f"Failed to extract memories: {e}", exc_info=True)
            return []
    
    async def get_all_memories(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的所有记忆"""
        if not self.memory:
            logger.debug("Memory instance is None, returning empty list")
            return []
        
        try:
            logger.debug(f"Getting all memories for user_id={user_id}, limit={limit}")
            # 直接调用，不使用线程池执行器，避免 SQLite 线程安全问题
            
            # 尝试使用 get_all 方法
            if hasattr(self.memory, 'get_all'):
                logger.debug("Using get_all method")
                memories = self.memory.get_all(user_id=user_id, limit=limit)
            # 或者使用 get_memories
            elif hasattr(self.memory, 'get_memories'):
                logger.debug("Using get_memories method")
                memories = self.memory.get_memories(user_id=user_id)
            else:
                # 如果没有这些方法，使用 search 搜索所有内容
                logger.debug("Using search method as fallback")
                memories = self.memory.search(query="", user_id=user_id, limit=limit)
            
            logger.debug(f"get_all_memories returned: {type(memories)}")
            
            if memories and "memories" in memories:
                logger.debug(f"Found {len(memories['memories'])} memories in result")
                return memories["memories"]
            elif isinstance(memories, list):
                logger.debug(f"Memories is a list with {len(memories)} items")
                return memories
            else:
                logger.warning(f"Unexpected memories format: {type(memories)}")
            return []
        except Exception as e:
            logger.error(f"Failed to get all memories: {e}", exc_info=True)
            return []
    
    async def get_relevant_memories(self, query: str, user_id: str, limit: int = 5) -> List[str]:
        """获取相关记忆"""
        if not self.memory:
            logger.debug("Memory instance is None, returning empty list")
            return []
        
        try:
            logger.debug(f"Searching memories: query={query[:50]}..., user_id={user_id}, limit={limit}")
            # 直接调用，不使用线程池执行器，避免 SQLite 线程安全问题
            memories = self.memory.search(query=query, user_id=user_id, limit=limit)
            
            logger.debug(f"Search returned: {type(memories)}, content preview: {str(memories)[:200]}")
            
            if memories and "memories" in memories:
                # 提取记忆文本
                result = [mem.get("memory", "") for mem in memories["memories"]]
                logger.debug(f"Extracted {len(result)} memories from search results")
                return result
            elif isinstance(memories, list):
                logger.debug(f"Memories is a list with {len(memories)} items")
                return memories
            else:
                logger.warning(f"Unexpected memories format: {type(memories)}")
            return []
        except Exception as e:
            # 打印当前配置信息用于调试
            logger.error(f"=== 记忆搜索失败时的配置信息 ===")
            logger.error(f"API Base URL: {os.getenv('OPENAI_BASE_URL', 'Not set')}")
            logger.error(f"API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
            logger.error(f"Embedding Model: {os.getenv('OPENAI_EMBEDDING_MODEL', 'Not set')}")
            logger.error(f"Search Query: {query[:50]}...")
            logger.error(f"User ID: {user_id}")
            logger.error(f"=====================================")
            
            # 如果是连接错误或认证错误，记录警告但不抛出异常
            if "Connection error" in str(e) or "Invalid token" in str(e) or "API" in str(e):
                logger.warning(f"Memory search failed due to API issues, skipping: {e}")
            else:
                logger.error(f"Failed to search memories: {e}", exc_info=True)
            return []
    
    async def add_memory(self, content: str, user_id: str, metadata: Optional[Dict[str, Any]] = None):
        """添加记忆"""
        logger.debug(f"add_memory called: content={content[:100]}..., user_id={user_id}, metadata={metadata}")
        
        if not self.memory:
            logger.warning("Memory instance is None, cannot add memory")
            return None
        
        try:
            logger.debug(f"Calling memory.add with content length={len(content)}")
            # 直接调用，不使用线程池执行器，避免 SQLite 线程安全问题
            result = self.memory.add(content, user_id=user_id, metadata=metadata or {})
            logger.info(f"Memory.add returned: {result}")
            
            if result:
                memory_id = result.get("id") if isinstance(result, dict) else str(result)
                logger.info(f"✓ Successfully added memory with id={memory_id}")
            else:
                logger.warning("Memory.add returned None or empty result")
            
            return result
        except Exception as e:
            # 打印当前配置信息用于调试
            logger.error(f"=== 记忆添加失败时的配置信息 ===")
            logger.error(f"API Base URL: {os.getenv('OPENAI_BASE_URL', 'Not set')}")
            logger.error(f"API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
            logger.error(f"Embedding Model: {os.getenv('OPENAI_EMBEDDING_MODEL', 'Not set')}")
            logger.error(f"Memory Content: {content[:50]}...")
            logger.error(f"User ID: {user_id}")
            logger.error(f"=====================================")
            
            # 如果是连接错误或认证错误，记录警告但不抛出异常
            if "Connection error" in str(e) or "Invalid token" in str(e) or "API" in str(e):
                logger.warning(f"Memory addition failed due to API issues, skipping: {e}")
            else:
                logger.error(f"Failed to add memory: {e}", exc_info=True)
            return None
    
    async def add_conversation_memories(self, user_input: str, assistant_reply: str, user_id: str, session_id: str):
        """智能添加对话记忆：提取关键信息而非完整对话"""
        if not self.memory:
            logger.warning("Memory manager not initialized, skipping memory addition")
            return
        
        try:
            logger.info(f"=== Adding conversation memories ===")
            logger.info(f"user_id={user_id}, session_id={session_id}")
            logger.info(f"user_input={user_input}")
            logger.info(f"assistant_reply length={len(assistant_reply)}")
            
            # 首先尝试直接添加用户输入（作为测试）
            # 如果用户输入包含明显的偏好信息，直接添加
            if any(keyword in user_input for keyword in ["喜欢", "不喜欢", "偏好", "讨厌", "热爱"]):
                logger.info("Detected preference keywords, adding direct memory")
                try:
                    direct_result = await self.add_memory(
                        content=user_input,
                        user_id=user_id,
                        metadata={
                            "type": "preference",
                            "importance": "medium",
                            "session_id": session_id,
                            "source": "conversation",
                            "method": "direct"
                        }
                    )
                    if direct_result:
                        logger.info(f"✓ Direct memory added successfully: {direct_result}")
                except Exception as e:
                    logger.error(f"Failed to add direct memory: {e}", exc_info=True)
            
            # 然后尝试提取关键记忆
            logger.info("Attempting to extract key memories using LLM...")
            key_memories = await self.extract_key_memories(user_input, assistant_reply)
            
            if not key_memories:
                logger.warning(f"No key memories extracted from conversation")
                logger.info("This might be normal if the conversation doesn't contain memorable information")
                return
            
            logger.info(f"Found {len(key_memories)} key memories to add")
            logger.debug(f"Key memories: {key_memories}")
            
            # 分别存储每条关键记忆
            added_count = 0
            for idx, memory_item in enumerate(key_memories):
                memory_type = memory_item.get("type", "fact")
                memory_content = memory_item.get("content", "")
                importance = memory_item.get("importance", "medium")
                
                logger.info(f"Processing memory {idx+1}/{len(key_memories)}: type={memory_type}, importance={importance}")
                logger.debug(f"Memory content: {memory_content}")
                
                if memory_content:
                    try:
                        result = await self.add_memory(
                            content=memory_content,
                            user_id=user_id,
                            metadata={
                                "type": memory_type,
                                "importance": importance,
                                "session_id": session_id,
                                "source": "conversation",
                                "method": "extracted"
                            }
                        )
                        if result:
                            added_count += 1
                            memory_id = result.get("id") if isinstance(result, dict) else str(result)
                            logger.info(f"✓ Added memory {added_count}/{len(key_memories)}: id={memory_id}, type={memory_type}, content={memory_content[:50]}...")
                        else:
                            logger.warning(f"✗ Failed to add memory (result is None): {memory_content[:50]}...")
                    except Exception as e:
                        logger.error(f"✗ Error adding memory {idx+1}: {e}", exc_info=True)
                else:
                    logger.warning(f"Memory item {idx+1} has empty content, skipping")
            
            logger.info(f"=== Memory addition completed: {added_count}/{len(key_memories)} memories added ===")
        except Exception as e:
            logger.error(f"✗ Failed to add conversation memories: {e}", exc_info=True)
    
    async def update_memory(self, memory_id: str, data: str):
        """更新记忆"""
        if not self.memory:
            return None
        
        try:
            result = self.memory.update(memory_id=memory_id, data=data)
            return result
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            return None
    
    async def add_conversation(self, messages: List[Dict[str, str]], user_id: str):
        """添加对话记忆（保留原方法以兼容）"""
        if not self.memory:
            return None
        
        try:
            # 将对话转换为文本格式
            conversation_text = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in messages
            ])
            result = self.memory.add(conversation_text, user_id=user_id, metadata={"type": "conversation"})
            return result
        except Exception as e:
            logger.error(f"Failed to add conversation memory: {e}")
            return None

# 全局记忆管理器实例
memory_manager = MemoryManager()
