"""
Domain models for the agentic integration platform.

This package contains all data models, database schemas, and domain entities
used throughout the application.
"""

from app.models.base import BaseModel, TimestampMixin
from app.models.integration import Integration, IntegrationStatus, IntegrationType
from app.models.knowledge import Entity, Relationship, Pattern
from app.models.ai import AIModel, AIProvider, ConversationSession, Message
from app.models.user import User, Role, Permission
from app.models.system import SystemConnection, APIEndpoint, DataMapping

__all__ = [
    # Base models
    "BaseModel",
    "TimestampMixin",
    
    # Integration models
    "Integration",
    "IntegrationStatus", 
    "IntegrationType",
    
    # Knowledge graph models
    "Entity",
    "Relationship",
    "Pattern",
    
    # AI models
    "AIModel",
    "AIProvider",
    "ConversationSession",
    "Message",
    
    # User models
    "User",
    "Role",
    "Permission",
    
    # System models
    "SystemConnection",
    "APIEndpoint",
    "DataMapping",
]
