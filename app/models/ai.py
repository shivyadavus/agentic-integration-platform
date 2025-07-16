"""
AI and conversation domain models for the agentic integration platform.

This module defines models for managing AI interactions, conversation sessions,
and Model Context Protocol (MCP) implementations.
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin, AuditMixin, MetadataMixin


class AIProvider(enum.Enum):
    """Supported AI model providers."""
    
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"


class MessageRole(enum.Enum):
    """Roles in AI conversations."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


class ConversationStatus(enum.Enum):
    """Status of conversation sessions."""
    
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ERROR = "error"


class AIModel(BaseModel, TimestampMixin, MetadataMixin):
    """
    AI model configuration and capabilities.
    
    Stores information about available AI models, their capabilities,
    and performance characteristics for integration generation.
    """
    
    __tablename__ = "ai_models"
    
    # Model Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[AIProvider] = mapped_column(
        Enum(AIProvider),
        nullable=False,
        index=True
    )
    model_id: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Capabilities
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    supports_function_calling: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_code_generation: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_json_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Performance Characteristics
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    tokens_per_second: Mapped[Optional[float]] = mapped_column(Float)
    cost_per_1k_tokens: Mapped[Optional[float]] = mapped_column(Float)
    
    # Usage Statistics
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # Configuration
    default_temperature: Mapped[float] = mapped_column(Float, default=0.1)
    default_top_p: Mapped[float] = mapped_column(Float, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def __repr__(self) -> str:
        return f"<AIModel(id={self.id}, name='{self.name}', provider={self.provider.value})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def record_usage(self, tokens_used: int, success: bool = True, response_time_ms: Optional[float] = None) -> None:
        """Record model usage statistics."""
        self.total_requests += 1
        self.total_tokens_used += tokens_used
        
        if success:
            self.successful_requests += 1
        
        if response_time_ms:
            # Update running average
            if self.avg_response_time_ms:
                self.avg_response_time_ms = (self.avg_response_time_ms + response_time_ms) / 2
            else:
                self.avg_response_time_ms = response_time_ms


class ConversationSession(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    Conversation session for Model Context Protocol (MCP) implementation.
    
    Maintains persistent context across multiple interactions with AI models,
    enabling conversational continuity and context-aware responses.
    """
    
    __tablename__ = "conversation_sessions"
    
    # Session Information
    title: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False,
        index=True
    )
    
    # Context Information
    context_summary: Mapped[Optional[str]] = mapped_column(Text)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    context_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # AI Model Configuration
    ai_model_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_models.id"),
        index=True
    )
    temperature: Mapped[float] = mapped_column(Float, default=0.1)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    
    # Session Statistics
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # User Context
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True
    )
    
    # Integration Context
    integration_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("integrations.id"),
        index=True
    )
    
    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation_session",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    ai_model: Mapped[Optional["AIModel"]] = relationship("AIModel")
    
    def __repr__(self) -> str:
        return f"<ConversationSession(id={self.id}, status={self.status.value}, messages={self.message_count})>"
    
    def add_message(self, role: MessageRole, content: str, **kwargs: Any) -> "Message":
        """Add a message to the conversation."""
        message = Message(
            conversation_session_id=self.id,
            role=role,
            content=content,
            **kwargs
        )
        self.message_count += 1
        return message
    
    def get_context_messages(self, limit: Optional[int] = None) -> List["Message"]:
        """Get recent messages for context."""
        messages = sorted(self.messages, key=lambda m: m.created_at)
        if limit:
            return messages[-limit:]
        return messages
    
    def update_context_summary(self, summary: str) -> None:
        """Update the context summary."""
        self.context_summary = summary
    
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == ConversationStatus.ACTIVE


class Message(BaseModel, TimestampMixin):
    """
    Individual message in a conversation session.
    
    Stores messages exchanged between users and AI models, including
    function calls, tool usage, and metadata for context management.
    """
    
    __tablename__ = "messages"
    
    # Conversation Context
    conversation_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation_sessions.id"),
        nullable=False,
        index=True
    )
    
    # Message Content
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Function/Tool Information
    function_name: Mapped[Optional[str]] = mapped_column(String(255))
    function_arguments: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    function_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Token Usage
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Processing Information
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    model_used: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Context and Metadata
    context_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Relationships
    conversation_session: Mapped["ConversationSession"] = relationship(
        "ConversationSession",
        back_populates="messages"
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role.value}, session_id={self.conversation_session_id})>"
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used in this message."""
        return (self.input_tokens or 0) + (self.output_tokens or 0)
    
    def is_function_call(self) -> bool:
        """Check if message is a function call."""
        return self.role == MessageRole.FUNCTION or self.function_name is not None
    
    def get_content_preview(self, max_length: int = 100) -> str:
        """Get truncated content for display."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
