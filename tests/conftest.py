"""
Pytest configuration and shared fixtures for the agentic integration platform.

This module provides common test fixtures, database setup, and configuration
for all test modules in the platform.
"""

import asyncio
import os
import sys
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Mock sentence_transformers to avoid heavy dependency in tests
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['sentence_transformers.SentenceTransformer'] = MagicMock()

# Set required environment variables before importing app modules
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("POSTGRES_PASSWORD", "test-postgres-password")
os.environ.setdefault("NEO4J_PASSWORD", "test-neo4j-password")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ENVIRONMENT", "test")

from app.core.config import Settings, get_settings
from app.database.session import get_db
from app.main import create_application
from app.models.base import Base


# Test settings override
class TestSettings(Settings):
    """Test-specific settings."""

    # Database (override parent fields)
    test_database_url: str = "sqlite+aiosqlite:///:memory:"

    # Required database fields
    postgres_password: str = "test-postgres-password"
    neo4j_password: str = "test-neo4j-password"

    # Disable external services for testing
    test_redis_url: str = "redis://localhost:6379/15"  # Use test DB
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"

    # AI Services (use mock keys for testing)
    anthropic_api_key: str = "test-anthropic-key"
    openai_api_key: str = "test-openai-key"

    # Security
    secret_key: str = "test-secret-key-for-testing-only"
    jwt_secret_key: str = "test-jwt-secret-key"

    # Environment
    environment: str = "test"
    debug: bool = True

    @property
    def database_url(self) -> str:
        """Override database URL for testing."""
        return self.test_database_url

    @property
    def redis_url(self) -> str:
        """Override Redis URL for testing."""
        return self.test_redis_url
    testing: bool = True

    class Config:
        env_file = None  # Don't load .env in tests


# Remove custom event loop fixture to avoid conflicts with pytest-asyncio


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    """Provide test settings."""
    return TestSettings()


@pytest.fixture(scope="session")
async def test_engine(test_settings: TestSettings):
    """Create test database engine."""
    engine = create_async_engine(
        test_settings.database_url,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 10  # Add timeout to prevent hanging
        },
        echo=False,
        pool_timeout=10,  # Connection pool timeout
        pool_recycle=300,  # Recycle connections
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,  # Prevent automatic flushing
        autocommit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            # Ensure session is properly closed
            await session.rollback()
            await session.close()


@pytest.fixture
def override_get_settings(test_settings: TestSettings):
    """Override settings dependency."""
    def _override_get_settings():
        return test_settings
    return _override_get_settings


@pytest.fixture
def override_get_db(test_db_session: AsyncSession):
    """Override database dependency."""
    async def _override_get_db():
        yield test_db_session
    return _override_get_db


@pytest.fixture
def test_app(override_get_settings, override_get_db):
    """Create test FastAPI application."""
    app = create_application()
    
    # Override dependencies
    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_db] = override_get_db
    
    yield app
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(test_app) -> TestClient:
    """Create test client."""
    return TestClient(test_app)


@pytest_asyncio.fixture
async def async_test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# Mock fixtures for external services
@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client."""
    mock = AsyncMock()
    mock.messages.create = AsyncMock()
    return mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock = AsyncMock()
    mock.chat.completions.create = AsyncMock()
    return mock


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver."""
    mock = MagicMock()
    mock.session = MagicMock()
    return mock


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client."""
    mock = AsyncMock()
    return mock


# Test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": "hashed_password_here",
        "is_active": True,
        "is_verified": True,
    }


@pytest.fixture
def sample_integration_data():
    """Sample integration data for testing."""
    return {
        "name": "Test Integration",
        "description": "A test integration for unit testing",
        "integration_type": "sync",
        "source_system": "salesforce",
        "target_system": "hubspot",
        "configuration": {
            "sync_frequency": "hourly",
            "fields_mapping": {
                "email": "email",
                "name": "full_name"
            }
        },
        "is_active": True,
    }


@pytest.fixture
def sample_entity_data():
    """Sample entity data for testing."""
    return {
        "name": "Customer",
        "entity_type": "business_object",
        "description": "Customer entity for CRM systems",
        "properties": {
            "fields": ["id", "email", "name", "created_at"],
            "primary_key": "id",
            "required_fields": ["email", "name"]
        },
        "confidence_score": 0.95,
    }


# Utility functions for tests
@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Markers for different test types
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
