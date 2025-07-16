"""
Main v1 API router that combines all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import integrations, knowledge, mcp

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    integrations.router, 
    prefix="/integrations", 
    tags=["integrations"]
)
api_router.include_router(
    knowledge.router, 
    prefix="/knowledge", 
    tags=["knowledge"]
)
api_router.include_router(
    mcp.router, 
    prefix="/mcp", 
    tags=["mcp"]
)
