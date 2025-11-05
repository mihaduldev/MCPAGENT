"""
Database models for persistent storage
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, 
    ForeignKey, Boolean, JSON, Float, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class User(Base):
    """User model for authentication and personalization"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    api_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # User preferences as JSON
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Conversation(Base):
    """Conversation/session model for tracking chat sessions"""
    
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Conversation mode (agent, rag, custom)
    mode: Mapped[str] = mapped_column(String(50), default="agent")
    
    # Agent configuration as JSON
    agent_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Conversation metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_session_active", "session_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, session_id='{self.session_id}', messages={len(self.messages)})>"


class Message(Base):
    """Message model for storing conversation messages"""
    
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    
    # Message content
    role: Mapped[str] = mapped_column(String(20))  # user, assistant, system, tool
    content: Mapped[str] = mapped_column(Text)
    
    # Tool usage tracking
    tool_calls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tool_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Token usage
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Cost tracking
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Performance metrics
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # RAG context used
    retrieved_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_conversation_created", "conversation_id", "created_at"),
        Index("idx_role_created", "role", "created_at"),
    )
    
    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, role='{self.role}', content='{preview}')>"


class Document(Base):
    """Document model for ingested documents in RAG system"""
    
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    
    # Document identification
    doc_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    filename: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    file_type: Mapped[str] = mapped_column(String(50))  # pdf, docx, txt, etc.
    file_size: Mapped[int] = mapped_column(Integer)  # bytes
    
    # Document content
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)  # SHA-256
    
    # Processing status
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, processing, completed, failed
    
    # Vector store info
    vector_store_ids: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )  # IDs in vector store
    chunk_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="documents")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_status_created", "status", "created_at"),
        Index("idx_content_hash", "content_hash"),
    )
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class APIKey(Base):
    """API Key model for service-to-service authentication"""
    
    __tablename__ = "api_keys"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Owner
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    
    # Permissions
    scopes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Rate limiting
    rate_limit_per_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Usage tracking
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name='{self.name}', active={self.is_active})>"

