from typing import Any, Dict, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..config import settings
from ..services.memory import memory_manager
import logging

logger = logging.getLogger(__name__)


class ConversationGraph:
    """
    最小版本：直接调用 OpenAI 兼容 API，后续可扩展为 LangGraph 编排。
    集成了 mem0 记忆管理。
    """

    def __init__(self) -> None:
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """延迟初始化 LLM"""
        if not settings.LLM_API_KEY:
            print("Warning: LLM_API_KEY 未配置，LLM 功能将不可用")
            return
        
        try:
            llm_kwargs = {
                "model": settings.LLM_MODEL_CHAT,
                "streaming": True,
                "temperature": 0.7,
            }
            if settings.LLM_API_BASE:
                llm_kwargs["base_url"] = settings.LLM_API_BASE
            if settings.LLM_API_KEY:
                llm_kwargs["api_key"] = settings.LLM_API_KEY
            
            self.llm = ChatOpenAI(**llm_kwargs)
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            self.llm = None

    async def _build_system_message(self, user_input: str, session_context: Dict[str, Any]) -> str:
        """构建系统消息，包含相关记忆"""
        base_system = "你是一个有帮助的AI助手。"
        
        # 获取用户ID
        session_id = session_context.get("session_id")
        if not session_id:
            logger.debug("No session_id in context, skipping memory retrieval")
            return base_system
        
        user_id = memory_manager.get_user_id(session_id)
        logger.debug(f"Building system message for session_id={session_id}, user_id={user_id}")
        
        # 获取相关记忆
        try:
            memories = await memory_manager.get_relevant_memories(user_input, user_id)
            logger.debug(f"Retrieved {len(memories)} relevant memories for query: {user_input[:50]}...")
            
            if memories:
                memory_context = "\n\n相关记忆：\n" + "\n".join([f"- {mem}" for mem in memories])
                logger.debug(f"Added {len(memories)} memories to system message")
                return base_system + memory_context
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}", exc_info=True)
        
        return base_system

    async def run_stream(self, user_input: str, session_context: Dict[str, Any]) -> AsyncIterator[str]:
        """流式返回回复"""
        logger.info(f"run_stream called: user_input={user_input[:100]}..., session_context={session_context}")
        
        if not self.llm:
            if not settings.LLM_API_KEY:
                logger.error("LLM_API_KEY not configured")
                yield "错误: LLM_API_KEY 未配置，请在 .env 文件中设置 LLM_API_KEY"
            else:
                logger.error("LLM initialization failed")
                yield "错误: LLM 初始化失败，请检查配置"
            return
        
        # 构建包含记忆的系统消息
        system_content = await self._build_system_message(user_input, session_context)
        logger.debug(f"System message length: {len(system_content)}")
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_input),
        ]
        
        full_response = ""
        session_id = session_context.get("session_id")
        try:
            logger.info(f"Starting LLM stream for session_id={session_id}")
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield chunk.content
            
            logger.info(f"LLM stream completed, response length: {len(full_response)}")
            
            # 对话结束后，将对话内容添加到记忆
            if session_id:
                user_id = memory_manager.get_user_id(session_id)
                logger.info(f"Attempting to add conversation memories: session_id={session_id}, user_id={user_id}")
                # 使用智能提取方法，只保存关键信息
                await memory_manager.add_conversation_memories(
                    user_input=user_input,
                    assistant_reply=full_response,
                    user_id=user_id,
                    session_id=session_id
                )
                logger.info(f"Memory addition process completed for session_id={session_id}")
            else:
                logger.warning("No session_id available, skipping memory addition")
        except Exception as e:
            logger.error(f"Error in run_stream: {e}", exc_info=True)
            yield f"错误: LLM调用失败 - {str(e)}"

    async def run(self, user_input: str, session_context: Dict[str, Any]) -> str:
        """非流式返回完整回复"""
        logger.info(f"run called: user_input={user_input[:100]}..., session_context={session_context}")
        
        if not self.llm:
            if not settings.LLM_API_KEY:
                logger.error("LLM_API_KEY not configured")
                return "错误: LLM_API_KEY 未配置，请在 .env 文件中设置 LLM_API_KEY"
            else:
                logger.error("LLM initialization failed")
                return "错误: LLM 初始化失败，请检查配置"
        
        # 构建包含记忆的系统消息
        system_content = await self._build_system_message(user_input, session_context)
        logger.debug(f"System message length: {len(system_content)}")
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_input),
        ]
        
        session_id = session_context.get("session_id")
        try:
            logger.info(f"Calling LLM invoke for session_id={session_id}")
            response = await self.llm.ainvoke(messages)
            reply = response.content
            logger.info(f"LLM response received, length: {len(reply)}")
            
            # 对话结束后，将对话内容添加到记忆
            if session_id:
                user_id = memory_manager.get_user_id(session_id)
                logger.info(f"Attempting to add conversation memories: session_id={session_id}, user_id={user_id}")
                # 使用智能提取方法，只保存关键信息
                await memory_manager.add_conversation_memories(
                    user_input=user_input,
                    assistant_reply=reply,
                    user_id=user_id,
                    session_id=session_id
                )
                logger.info(f"Memory addition process completed for session_id={session_id}")
            else:
                logger.warning("No session_id available, skipping memory addition")
            
            return reply
        except Exception as e:
            logger.error(f"Error in run: {e}", exc_info=True)
            return f"错误: LLM调用失败 - {str(e)}"


