"""
Pytest configuration and fixtures
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from src.config import settings
from src.infrastructure.database import Base, get_db
from src.api.main import app


# ─────────────────────────────────────────────────────────────────────────────
# Database Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    # Use in-memory SQLite for tests
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create database session for tests"""
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ─────────────────────────────────────────────────────────────────────────────
# API Client Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def client(db_session) -> TestClient:
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Get authentication headers for tests"""
    return {
        "Authorization": f"Bearer {settings.api_keys[0]}"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Mock Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    return {
        "content": "This is a mock response",
        "model": "gpt-4",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


@pytest.fixture
def sample_document():
    """Sample document for testing"""
    return {
        "filename": "test.pdf",
        "content": "This is a test document content",
        "metadata": {"author": "Test User"}
    }


@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return {
        "message": "What is artificial intelligence?",
        "session_id": "test-session",
        "mode": "agent"
    }

