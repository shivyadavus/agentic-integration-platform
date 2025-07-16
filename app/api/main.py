"""
Main API router that combines all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import api_router as api_v1_router

api_router = APIRouter()

# Include v1 API routes (no prefix since main.py already adds /api/v1)
api_router.include_router(api_v1_router)
