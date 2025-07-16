"""
Dependency injection for FastAPI endpoints.
"""

from typing import AsyncGenerator
import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal
from app.services.ai.factory import AIServiceFactory
from app.services.knowledge.graph_service import KnowledgeGraphService
from app.services.knowledge.vector_service import VectorService
from app.services.knowledge.pattern_service import PatternService

logger = logging.getLogger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_ai_service():
    """Get AI service instance."""
    return AIServiceFactory.get_default_service()


# Global knowledge graph service instance
_kg_service_instance = None

async def get_knowledge_graph_service():
    """Get knowledge graph service instance (singleton)."""
    global _kg_service_instance
    if _kg_service_instance is None:
        _kg_service_instance = KnowledgeGraphService()
        try:
            await _kg_service_instance.initialize()
        except Exception as e:
            # If initialization fails, return None to avoid recursion
            logger.warning(f"Knowledge graph initialization failed: {e}")
            return None
    return _kg_service_instance


async def get_vector_service():
    """Get vector service instance."""
    service = VectorService()
    await service.initialize()
    return service


async def get_pattern_service(
    vector_service: VectorService = Depends(get_vector_service)
):
    """Get pattern service instance."""
    return PatternService(vector_service=vector_service)
