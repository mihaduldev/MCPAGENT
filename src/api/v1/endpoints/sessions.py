"""
Session management endpoints for API v1
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.api.v1.models.requests import SessionCreateRequest
from src.api.v1.models.responses import SessionResponse, MessageResponse
from src.infrastructure.database import get_db, Conversation, Message
from src.config.logging import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, tags=["sessions"])
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db)
) -> SessionResponse:
    """Create a new chat session"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
        
        # Check if session already exists
        existing = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Session '{session_id}' already exists")
        
        # Create new session
        conversation = Conversation(
            session_id=session_id,
            mode=request.mode,
            title=request.title,
            is_active=True
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return SessionResponse(
            session_id=conversation.session_id,
            mode=conversation.mode,
            title=conversation.title,
            message_count=0,
            created_at=conversation.created_at,
            is_active=conversation.is_active
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session creation error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse, tags=["sessions"])
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> SessionResponse:
    """Get session information"""
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    message_count = db.query(Message).filter(Message.conversation_id == conversation.id).count()
    
    return SessionResponse(
        session_id=conversation.session_id,
        mode=conversation.mode,
        title=conversation.title,
        message_count=message_count,
        created_at=conversation.created_at,
        is_active=conversation.is_active
    )


@router.get("/sessions", response_model=List[SessionResponse], tags=["sessions"])
async def list_sessions(
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
) -> List[SessionResponse]:
    """List all sessions"""
    conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for conv in conversations:
        message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
        result.append(SessionResponse(
            session_id=conv.session_id,
            mode=conv.mode,
            title=conv.title,
            message_count=message_count,
            created_at=conv.created_at,
            is_active=conv.is_active
        ))
    
    return result


@router.delete("/sessions/{session_id}", tags=["sessions"])
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a session and all its messages"""
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    try:
        db.delete(conversation)
        db.commit()
        return {"status": "success", "message": f"Session '{session_id}' deleted"}
    except Exception as e:
        logger.error(f"Session deletion error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse], tags=["sessions"])
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    limit: int = 50
) -> List[MessageResponse]:
    """Get messages for a session"""
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).limit(limit).all()
    
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            tokens_used=msg.total_tokens
        )
        for msg in messages
    ]

