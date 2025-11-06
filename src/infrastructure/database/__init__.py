"""Database infrastructure"""

from .base import Base, get_db, engine, SessionLocal
from .models import User, Conversation, Message, Document


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


__all__ = [
    "Base",
    "get_db",
    "engine",
    "SessionLocal",
    "init_db",
    "User",
    "Conversation", 
    "Message",
    "Document"
]

