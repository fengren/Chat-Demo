from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ..config import settings


async def generate_summary(user_message: str, assistant_reply: str = None) -> str:
    """生成对话摘要作为会话标题"""
    # 如果 LLM 未配置，使用截取前50字符作为标题
    if not settings.LLM_API_KEY:
        summary = user_message.strip()[:50]
        return summary + ("..." if len(user_message) > 50 else "")
    
    try:
        # 创建临时 LLM 实例用于生成摘要
        llm_kwargs = {
            "model": settings.LLM_MODEL_CHAT,
            "temperature": 0.3,  # 降低温度以获得更稳定的摘要
        }
        if settings.LLM_API_BASE:
            llm_kwargs["base_url"] = settings.LLM_API_BASE
        if settings.LLM_API_KEY:
            llm_kwargs["api_key"] = settings.LLM_API_KEY
        
        llm = ChatOpenAI(**llm_kwargs)
        
        # 使用 LLM 生成摘要
        prompt = f"""请为以下对话生成一个简洁的标题（不超过15字，只返回标题，不要其他文字）：

用户：{user_message[:200]}
{'助手：' + assistant_reply[:200] if assistant_reply else ''}

标题："""
        
        messages = [HumanMessage(content=prompt)]
        
        try:
            response = await llm.ainvoke(messages)
            summary = response.content.strip()
            # 清理可能的多余文字
            summary = summary.replace("标题：", "").replace("标题", "").strip()
            # 限制长度
            if len(summary) > 50:
                summary = summary[:50]
            if not summary:
                summary = user_message.strip()[:50]
            return summary
        except Exception as e:
            print(f"Failed to generate summary with LLM: {e}")
            # 降级到截取
            summary = user_message.strip()[:50]
            return summary + ("..." if len(user_message) > 50 else "")
    except Exception as e:
        print(f"Error generating summary: {e}")
        summary = user_message.strip()[:50]
        return summary + ("..." if len(user_message) > 50 else "")

