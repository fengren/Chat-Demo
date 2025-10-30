from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import logging
from ..lang.graph import ConversationGraph
from ..services.session import create_session as create_session_service, get_session, update_session_title as update_session_title_service
from ..services.message import save_message, count_messages_by_session
from ..services.summary import generate_summary

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/chat", tags=["chat"])
graph = ConversationGraph()


class ChatRequest(BaseModel):
    session_id: str = None
    content: str


@router.post("")
async def chat(body: ChatRequest):
    """非流式聊天接口"""
    logger.info(f"Chat request received: session_id={body.session_id}, content_length={len(body.content)}")
    try:
        # 确保 session 存在
        if not body.session_id:
            logger.info("No session_id provided, creating new session")
            session = create_session_service()
            body.session_id = session["id"]
            logger.info(f"Created new session: {body.session_id}")
        else:
            session = get_session(body.session_id)
            if not session:
                logger.warning(f"Session {body.session_id} not found, creating new one")
                session = create_session_service()
                body.session_id = session["id"]
        
        # 保存用户消息
        logger.debug(f"Saving user message to session {body.session_id}")
        save_message(body.session_id, "user", body.content)
        
        # 获取回复
        logger.info(f"Calling graph.run for session {body.session_id}")
        reply = await graph.run(body.content, {"session_id": body.session_id})
        logger.info(f"Received reply, length: {len(reply)}")
        
        # 保存助手消息
        logger.debug(f"Saving assistant message to session {body.session_id}")
        save_message(body.session_id, "assistant", reply)
        
        # 检查是否是首次对话
        message_count = count_messages_by_session(body.session_id)
        logger.debug(f"Message count for session {body.session_id}: {message_count}")
        if message_count == 2:  # 用户消息 + 助手消息
            # 首次对话，生成摘要并更新标题
            try:
                logger.info(f"First conversation, generating summary for session {body.session_id}")
                summary = await generate_summary(body.content, reply)
                update_session_title_service(body.session_id, summary)
                logger.info(f"Updated session title: {summary}")
            except Exception as e:
                logger.error(f"Failed to generate summary: {e}", exc_info=True)
        
        logger.info(f"Chat request completed successfully for session {body.session_id}")
        return {"reply": reply, "session_id": body.session_id}
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/stream")
async def chat_stream(request: Request, session_id: str = None, q: str = ""):
    """流式聊天接口（SSE）"""
    logger.info(f"Chat stream request: session_id={session_id}, query_length={len(q)}")
    
    if not q:
        logger.debug("Empty query, returning empty generator")
        async def empty_generator():
            yield b"event: done\n\n"
        return StreamingResponse(empty_generator(), media_type="text/event-stream")
    
    async def event_generator():
        full_reply = ""
        current_session_id = session_id  # 使用局部变量，避免作用域问题
        
        try:
            logger.info(f"Starting event generator for session_id={current_session_id}")
            
            # 确保 session 存在，如果没有则创建新的
            if not current_session_id or current_session_id == '':
                logger.info("No session_id, creating new session")
                session = create_session_service()
                current_session_id = session["id"]
                logger.info(f"Created new session: {current_session_id}")
                yield f"data: {json.dumps({'session_id': current_session_id})}\n\n".encode("utf-8")
            else:
                # 验证 session 是否存在
                session = get_session(current_session_id)
                if not session:
                    # 如果 session 不存在，创建新的
                    logger.warning(f"Session {current_session_id} not found, creating new one")
                    session = create_session_service()
                    current_session_id = session["id"]
                    yield f"data: {json.dumps({'session_id': current_session_id})}\n\n".encode("utf-8")
            
            # 保存用户消息
            try:
                logger.debug(f"Saving user message to session {current_session_id}")
                save_message(current_session_id, "user", q)
            except Exception as e:
                logger.error(f"Failed to save user message: {e}", exc_info=True)
            
            # 流式获取回复并累积
            try:
                logger.info(f"Starting LLM stream for session {current_session_id}")
                async for chunk in graph.run_stream(q, {"session_id": current_session_id}):
                    if await request.is_disconnected():
                        logger.warning("Client disconnected during stream")
                        break
                    full_reply += chunk
                    payload = json.dumps({"delta": chunk})
                    yield f"data: {payload}\n\n".encode("utf-8")
                
                logger.info(f"LLM stream completed, total length: {len(full_reply)}")
            except Exception as e:
                logger.error(f"Error in LLM stream: {e}", exc_info=True)
                error_payload = json.dumps({"error": f"LLM调用失败: {str(e)}"})
                yield f"data: {error_payload}\n\n".encode("utf-8")
            
            # 流式结束后保存完整助手消息
            if full_reply:
                try:
                    logger.debug(f"Saving assistant message to session {current_session_id}")
                    save_message(current_session_id, "assistant", full_reply)
                    
                    # 检查是否是首次对话（用户消息 + 助手消息 = 2条消息）
                    message_count = count_messages_by_session(current_session_id)
                    logger.debug(f"Message count: {message_count}")
                    if message_count == 2:
                        # 首次对话，生成摘要并更新标题
                        try:
                            logger.info(f"First conversation, generating summary")
                            summary = await generate_summary(q, full_reply)
                            update_session_title_service(current_session_id, summary)
                            logger.info(f"Updated session title: {summary}")
                            # 发送标题更新事件
                            yield f"data: {json.dumps({'title_update': summary})}\n\n".encode("utf-8")
                        except Exception as e:
                            logger.error(f"Failed to generate summary: {e}", exc_info=True)
                except Exception as e:
                    logger.error(f"Failed to save assistant message: {e}", exc_info=True)
            
            logger.info(f"Event generator completed for session {current_session_id}")
            yield b"event: done\n\n"
        except Exception as e:
            import traceback
            error_msg = f"服务器错误: {str(e)}"
            logger.error(f"Error in chat_stream: {traceback.format_exc()}")
            error_payload = json.dumps({"error": error_msg})
            yield f"data: {error_payload}\n\n".encode("utf-8")
            yield b"event: done\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    })
