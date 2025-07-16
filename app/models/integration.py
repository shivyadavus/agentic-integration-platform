"""
Integration domain models for the agentic integration platform.

This module defines the core integration entities including Integration,
IntegrationStatus, and related models for managing AI-generated integrations.
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin, AuditMixin, MetadataMixin


class AIProvider(enum.Enum):
    """AI providers that match the database enum."""
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GOOGLE = "GOOGLE"
    AZURE = "AZURE"
    AWS = "AWS"
    HUGGINGFACE = "HUGGINGFACE"


class IntegrationStatus(enum.Enum):
    """Status of an integration throughout its lifecycle."""
    
    DRAFT = "draft"                    # Initial creation, not yet processed
    ANALYZING = "analyzing"            # AI is analyzing requirements
    GENERATING = "generating"          # Code generation in progress
    VALIDATING = "validating"          # Semantic validation in progress
    TESTING = "testing"               # Testing in sandbox environment
    READY = "ready"                   # Ready for deployment
    DEPLOYING = "deploying"           # Deployment in progress
    ACTIVE = "active"                 # Successfully deployed and running
    PAUSED = "paused"                 # Temporarily paused
    ERROR = "error"                   # Error occurred during processing
    FAILED = "failed"                 # Failed validation or deployment
    ARCHIVED = "archived"             # Archived/deprecated


class IntegrationType(enum.Enum):
    """Type of integration based on data flow pattern."""
    
    SYNC = "sync"                     # Synchronous data synchronization
    ASYNC = "async"                   # Asynchronous data processing
    WEBHOOK = "webhook"               # Webhook-based integration
    BATCH = "batch"                   # Batch data processing
    REALTIME = "realtime"             # Real-time streaming
    API_PROXY = "api_proxy"           # API proxy/gateway
    ETL = "etl"                       # Extract, Transform, Load
    EVENT_DRIVEN = "event_driven"     # Event-driven architecture


class Integration(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    Core integration model representing an AI-generated integration.
    
    This model stores the complete lifecycle of an integration from natural
    language specification to deployed code.
    """
    
    __tablename__ = "integrations"
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    natural_language_spec: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status and Type
    status: Mapped[IntegrationStatus] = mapped_column(
        Enum(IntegrationStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=IntegrationStatus.DRAFT,
        nullable=False,
        index=True
    )
    integration_type: Mapped[IntegrationType] = mapped_column(
        Enum(IntegrationType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True
    )
    
    # AI Processing
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100))
    ai_provider: Mapped[Optional[AIProvider]] = mapped_column(Enum(AIProvider))
    processing_time_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Generated Code
    generated_code: Mapped[Optional[str]] = mapped_column(Text)
    code_language: Mapped[str] = mapped_column(String(50), default="python")
    code_version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Validation Results
    validation_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    validation_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Testing Results
    test_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    test_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Deployment Information
    deployment_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    deployment_url: Mapped[Optional[str]] = mapped_column(String(500))
    deployed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Performance Metrics
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_execution_time_ms: Mapped[Optional[float]] = mapped_column()
    
    # Relationships
    source_system_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("system_connections.id"),
        index=True
    )
    target_system_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("system_connections.id"),
        index=True
    )
    conversation_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation_sessions.id"),
        index=True
    )
    
    # Relationships (will be defined when related models are created)
    executions: Mapped[List["IntegrationExecution"]] = relationship(
        "IntegrationExecution",
        back_populates="integration",
        cascade="all, delete-orphan"
    )
    versions: Mapped[List["IntegrationVersion"]] = relationship(
        "IntegrationVersion",
        back_populates="integration",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Integration(id={self.id}, name='{self.name}', status={self.status.value})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.execution_count == 0:
            return 0.0
        return (self.success_count / self.execution_count) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.execution_count == 0:
            return 0.0
        return (self.error_count / self.execution_count) * 100
    
    def is_deployable(self) -> bool:
        """Check if integration is ready for deployment."""
        return (
            self.status == IntegrationStatus.READY and
            self.validation_passed and
            self.test_passed and
            self.generated_code is not None
        )
    
    def is_active(self) -> bool:
        """Check if integration is currently active."""
        return self.status == IntegrationStatus.ACTIVE
    
    def can_execute(self) -> bool:
        """Check if integration can be executed."""
        return self.status in [IntegrationStatus.ACTIVE, IntegrationStatus.READY]


class IntegrationExecution(BaseModel, TimestampMixin):
    """
    Model for tracking individual integration executions.
    
    Stores execution history, performance metrics, and error details
    for monitoring and debugging purposes.
    """
    
    __tablename__ = "integration_executions"
    
    # Relationships
    integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("integrations.id"),
        nullable=False,
        index=True
    )
    
    # Execution Details
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Input/Output Data
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Error Information
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_type: Mapped[Optional[str]] = mapped_column(String(100))
    stack_trace: Mapped[Optional[str]] = mapped_column(Text)
    
    # Context Information
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Relationships
    integration: Mapped["Integration"] = relationship(
        "Integration",
        back_populates="executions"
    )
    
    def __repr__(self) -> str:
        return f"<IntegrationExecution(id={self.id}, integration_id={self.integration_id}, status='{self.status}')>"
    
    @property
    def was_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == "success"
    
    @property
    def had_error(self) -> bool:
        """Check if execution had an error."""
        return self.status == "error"


class IntegrationVersion(BaseModel, TimestampMixin, AuditMixin):
    """
    Model for tracking integration versions and changes.
    
    Maintains a history of all changes to integrations for rollback
    and audit purposes.
    """
    
    __tablename__ = "integration_versions"
    
    # Relationships
    integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("integrations.id"),
        nullable=False,
        index=True
    )
    
    # Version Information
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    change_description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Snapshot Data
    snapshot_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Relationships
    integration: Mapped["Integration"] = relationship(
        "Integration",
        back_populates="versions"
    )
    
    def __repr__(self) -> str:
        return f"<IntegrationVersion(id={self.id}, integration_id={self.integration_id}, version={self.version_number})>"
