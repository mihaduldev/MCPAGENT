"""
Response models for API v1
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    mode: str = Field(..., description="Operation mode used")
    tools_used: List[str] = Field(default_factory=list, description="Tools used in response")
    tokens_used: Optional[int] = Field(default=None, description="Total tokens used")
    cost_usd: Optional[float] = Field(default=None, description="Estimated cost in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Artificial intelligence (AI) is...",
                "session_id": "user-123",
                "mode": "agent",
                "tools_used": ["retrieve_dosiblog_context"],
                "tokens_used": 150,
                "cost_usd": 0.0003
            }
        }


class SessionResponse(BaseModel):
    """Session response model"""
    session_id: str
    mode: str
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    is_active: bool


class MessageResponse(BaseModel):
    """Message response model"""
    id: int
    role: str
    content: str
    created_at: datetime
    tokens_used: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    services: dict
    timestamp: float


class ErrorResponse(BaseModel):
    """Error response model"""
    error: dict = Field(..., description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "type": "validation_error",
                    "message": "Invalid request data",
                    "details": []
                }
            }
        }

