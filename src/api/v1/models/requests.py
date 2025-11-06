"""
Request models for API v1
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1)
    session_id: str = Field(default="default", description="Session ID for conversation history")
    mode: Literal["agent", "rag"] = Field(default="agent", description="Operation mode")
    agent_type: Optional[str] = Field(default=None, description="Specific agent type to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is artificial intelligence?",
                "session_id": "user-123",
                "mode": "agent"
            }
        }


class DocumentUploadRequest(BaseModel):
    """Document upload metadata"""
    title: Optional[str] = Field(default=None, description="Document title")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class SessionCreateRequest(BaseModel):
    """Create new session request"""
    session_id: Optional[str] = Field(default=None, description="Custom session ID")
    mode: Literal["agent", "rag"] = Field(default="agent", description="Default mode")
    title: Optional[str] = Field(default=None, description="Session title")

