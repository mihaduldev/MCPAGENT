"""
Chat endpoints for API v1
"""

import time
import asyncio
import json
from typing import AsyncGenerator, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from src.api.v1.models.requests import ChatRequest
from src.api.v1.models.responses import ChatResponse
from src.infrastructure.database import get_db, Conversation, Message
from src.config.logging import get_logger
from src.config import settings
from src.core.agent import AgentType, orchestrator
from src.core.rag import rag_system
from src.infrastructure.llm.llm_factory import create_llm
from src.core.mcp import load_mcp_tools
from src.utils.token_usage import get_token_usage_and_cost

logger = get_logger(__name__)

router = APIRouter()


def _get_or_create_conversation(db: Session, session_id: str, mode: str) -> Conversation:
    """Get or create conversation for session"""
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if not conversation:
        conversation = Conversation(
            session_id=session_id,
            mode=mode,
            is_active=True
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    return conversation


def _load_conversation_history(db: Session, conversation_id: int) -> List[BaseMessage]:
    """Load conversation history as LangChain messages"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    history = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            history.append(AIMessage(content=msg.content))
    
    return history


def _save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    tool_calls: Optional[dict] = None,
    tokens: Optional[int] = None,
    cost: Optional[float] = None
) -> Message:
    """Save message to database"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        total_tokens=tokens,
        cost_usd=cost
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


async def _initialize_agents():
    """Initialize agents with MCP tools if not already done"""
    if not orchestrator.agents:
        try:
            # Load MCP tools
            tools = await load_mcp_tools()
            logger.info(f"Loaded {len(tools)} MCP tools")
        except Exception as e:
            logger.warning(f"Failed to load MCP tools: {e}. Agent will work without tools.")
            tools = []
        
        try:
            # Register a general agent (with or without tools)
            from src.core.agent import Agent
            general_agent = Agent(
                agent_type=AgentType.GENERAL,
                tools=tools,
                name="General Assistant",
                description="General-purpose AI assistant with access to various tools"
            )
            orchestrator.register_agent(general_agent)
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}. Will fallback to direct LLM calls.")
            # Don't raise - allow fallback to direct LLM


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Chat endpoint - non-streaming
    
    Send a message to the AI agent and get a response.
    """
    start_time = time.time()
    
    try:
        # Get or create conversation
        conversation = _get_or_create_conversation(db, request.session_id, request.mode)
        
        # Load conversation history BEFORE saving current message (to avoid duplication)
        history = _load_conversation_history(db, conversation.id)
        
        # Save user message
        _save_message(db, conversation.id, "user", request.message)
        
        # Initialize agents if needed
        await _initialize_agents()
        
        response_text = ""
        tools_used = []
        tokens_used = None
        cost_usd = None
        
        if request.mode == "rag":
            # Use RAG system
            if not rag_system.available:
                raise HTTPException(
                    status_code=503,
                    detail="RAG system is not available. Please configure OpenAI API key."
                )
            
            llm = create_llm(streaming=False)
            response_text = await rag_system.query_with_history(
                query=request.message,
                session_id=request.session_id,
                llm=llm,
                history_manager=None  # Can be enhanced with proper history manager
            )
            
            # Note: RAG system doesn't return response object directly, 
            # so we can't extract token usage easily. This could be enhanced.
        
        elif request.mode == "agent":
            # Use agent system
            if orchestrator.agents:
                agent_type = None
                if request.agent_type:
                    try:
                        agent_type = AgentType(request.agent_type)
                    except ValueError:
                        logger.warning(f"Invalid agent_type: {request.agent_type}")
                
                # Route to agent
                result = await orchestrator.route_query(
                    query=request.message,
                    agent_type=agent_type,
                    history=history
                )
                
                response_text = result.get("response", "No response generated")
                tools_used = result.get("tools_used", [])
                
                # Extract token usage and cost from agent result
                token_usage = result.get("token_usage")
                if token_usage:
                    prompt_tokens = token_usage.get("prompt_tokens", 0)
                    completion_tokens = token_usage.get("completion_tokens", 0)
                    tokens_used = token_usage.get("total_tokens", prompt_tokens + completion_tokens)
                    
                    # Calculate cost
                    from src.utils.token_usage import calculate_cost
                    cost_usd = calculate_cost(
                        prompt_tokens,
                        completion_tokens,
                        model=settings.openai_model,
                        provider=settings.llm_provider
                    )
                else:
                    # Try to get from LLM response if available
                    # Note: Agent executor may not expose token usage directly
                    pass
            else:
                # Fallback to direct LLM if no agents available
                logger.info("No agents available, using direct LLM call")
                llm = create_llm(streaming=False)
                # Add current message to history for LLM
                messages = history + [HumanMessage(content=request.message)]
                response = await llm.ainvoke(messages)
                response_text = response.content if hasattr(response, 'content') else str(response)
                tools_used = []
                
                # Extract token usage and cost
                tokens_used, cost_usd = get_token_usage_and_cost(
                    response, 
                    model=getattr(llm, 'model_name', None) or settings.openai_model,
                    provider=settings.llm_provider
                )
        
        else:
            # Fallback: Simple LLM call
            llm = create_llm(streaming=False)
            # Add current message to history for LLM
            messages = history + [HumanMessage(content=request.message)]
            response = await llm.ainvoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Extract token usage and cost
            tokens_used, cost_usd = get_token_usage_and_cost(
                response,
                model=getattr(llm, 'model_name', None) or settings.openai_model,
                provider=settings.llm_provider
            )
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Save assistant response
        assistant_msg = _save_message(
            db,
            conversation.id,
            "assistant",
            response_text,
            tool_calls={"tools": tools_used} if tools_used else None,
            tokens=tokens_used,
            cost=cost_usd
        )
        
        # Update conversation metadata if needed
        if not conversation.title and len(request.message) < 100:
            conversation.title = request.message[:100]
            db.commit()
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            mode=request.mode,
            tools_used=tools_used,
            tokens_used=tokens_used,
            cost_usd=cost_usd
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream", tags=["chat"])
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint - streaming with Server-Sent Events
    
    Stream the AI response in real-time.
    """
    async def generate() -> AsyncGenerator[str, None]:
        full_response = ""
        tools_used = []
        
        try:
            # Get or create conversation
            conversation = _get_or_create_conversation(db, request.session_id, request.mode)
            
            # Load conversation history BEFORE saving current message (to avoid duplication)
            history = _load_conversation_history(db, conversation.id)
            
            # Save user message
            _save_message(db, conversation.id, "user", request.message)
            
            # Initialize agents if needed
            await _initialize_agents()
            
            if request.mode == "rag":
                # RAG streaming
                if not rag_system.available:
                    yield f"data: {json.dumps({'error': 'RAG system not available'})}\n\n"
                    return
                
                llm = create_llm(streaming=True)
                # For RAG, we'll stream the LLM response
                # Add current message to history for LLM
                messages = history + [HumanMessage(content=request.message)]
                
                async for chunk in llm.astream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        content = chunk.content
                        full_response += content
                        yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                
            elif request.mode == "agent":
                # Agent mode - use agent if available, otherwise fallback to LLM
                if orchestrator.agents:
                    # Use agent (non-streaming for now, then stream the result)
                    agent_type = None
                    if request.agent_type:
                        try:
                            from src.core.agent import AgentType
                            agent_type = AgentType(request.agent_type)
                        except:
                            pass
                    
                    result = await orchestrator.route_query(
                        query=request.message,
                        agent_type=agent_type,
                        history=history
                    )
                    
                    response_text = result.get("response", "")
                    tools_used = result.get("tools_used", [])
                    
                    # Stream the response character by character for better UX
                    for char in response_text:
                        full_response += char
                        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
                        await asyncio.sleep(0.01)  # Small delay for streaming effect
                else:
                    # Fallback to LLM streaming if no agents available
                    llm = create_llm(streaming=True)
                    # Add current message to history for LLM
                    messages = history + [HumanMessage(content=request.message)]
                    
                    async for chunk in llm.astream(messages):
                        if hasattr(chunk, 'content') and chunk.content:
                            content = chunk.content
                            full_response += content
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            
            else:
                # Simple LLM streaming
                llm = create_llm(streaming=True)
                # Add current message to history for LLM
                messages = history + [HumanMessage(content=request.message)]
                
                async for chunk in llm.astream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        content = chunk.content
                        full_response += content
                        yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            
            # Save assistant response
            _save_message(
                db,
                conversation.id,
                "assistant",
                full_response,
                tool_calls={"tools": tools_used} if tools_used else None
            )
            
            # Send final metadata
            yield f"data: {json.dumps({'type': 'done', 'tools_used': tools_used})}\n\n"
            yield "data: [DONE]\n\n"
        
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            db.rollback()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        }
    )

