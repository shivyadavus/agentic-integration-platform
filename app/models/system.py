"""
System and external service domain models for the agentic integration platform.

This module defines models for managing external system connections,
API endpoints, data mappings, and integration configurations.
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin, AuditMixin, MetadataMixin


class SystemType(enum.Enum):
    """Types of external systems."""
    
    CRM = "crm"                    # Customer Relationship Management
    ERP = "erp"                    # Enterprise Resource Planning
    ECOMMERCE = "ecommerce"        # E-commerce platforms
    MARKETING = "marketing"        # Marketing automation
    ANALYTICS = "analytics"        # Analytics platforms
    DATABASE = "database"          # Database systems
    API = "api"                    # Generic API services
    WEBHOOK = "webhook"            # Webhook endpoints
    FILE_STORAGE = "file_storage"  # File storage services
    MESSAGING = "messaging"        # Messaging/communication
    PAYMENT = "payment"            # Payment processing
    CUSTOM = "custom"              # Custom systems


class AuthenticationType(enum.Enum):
    """Authentication methods for external systems."""
    
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    JWT = "jwt"
    CUSTOM = "custom"


class ConnectionStatus(enum.Enum):
    """Status of system connections."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"
    PENDING = "pending"


class SystemConnection(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    External system connection configuration.
    
    Stores connection details, authentication information, and
    configuration for integrating with external systems.
    """
    
    __tablename__ = "system_connections"
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    system_type: Mapped[SystemType] = mapped_column(
        Enum(SystemType),
        nullable=False,
        index=True
    )
    
    # Connection Details
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_version: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Authentication
    auth_type: Mapped[AuthenticationType] = mapped_column(
        Enum(AuthenticationType),
        default=AuthenticationType.API_KEY,
        nullable=False
    )
    auth_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Status and Health
    status: Mapped[ConnectionStatus] = mapped_column(
        Enum(ConnectionStatus),
        default=ConnectionStatus.PENDING,
        nullable=False,
        index=True
    )
    last_health_check: Mapped[Optional[datetime]] = mapped_column()
    health_check_interval_minutes: Mapped[int] = mapped_column(default=60)
    
    # Rate Limiting
    rate_limit_requests_per_minute: Mapped[Optional[int]] = mapped_column()
    rate_limit_requests_per_hour: Mapped[Optional[int]] = mapped_column()
    
    # Configuration
    connection_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    headers: Mapped[Optional[Dict[str, str]]] = mapped_column(JSONB)
    timeout_seconds: Mapped[int] = mapped_column(default=30)
    
    # Usage Statistics
    total_requests: Mapped[int] = mapped_column(default=0)
    successful_requests: Mapped[int] = mapped_column(default=0)
    failed_requests: Mapped[int] = mapped_column(default=0)
    
    # Organization Context
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True
    )
    
    # Relationships
    api_endpoints: Mapped[List["APIEndpoint"]] = relationship(
        "APIEndpoint",
        back_populates="system_connection",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<SystemConnection(id={self.id}, name='{self.name}', type={self.system_type.value})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def is_healthy(self) -> bool:
        """Check if system connection is healthy."""
        return self.status == ConnectionStatus.ACTIVE
    
    def needs_health_check(self) -> bool:
        """Check if health check is needed."""
        if not self.last_health_check:
            return True
        
        time_since_check = datetime.utcnow() - self.last_health_check
        return time_since_check.total_seconds() > (self.health_check_interval_minutes * 60)
    
    def record_request(self, success: bool = True) -> None:
        """Record API request statistics."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        headers = {}
        
        if self.auth_type == AuthenticationType.API_KEY:
            if self.auth_config and "api_key" in self.auth_config:
                key_name = self.auth_config.get("key_name", "X-API-Key")
                headers[key_name] = self.auth_config["api_key"]
        
        elif self.auth_type == AuthenticationType.BEARER_TOKEN:
            if self.auth_config and "token" in self.auth_config:
                headers["Authorization"] = f"Bearer {self.auth_config['token']}"
        
        elif self.auth_type == AuthenticationType.BASIC_AUTH:
            if self.auth_config and "username" in self.auth_config and "password" in self.auth_config:
                import base64
                credentials = f"{self.auth_config['username']}:{self.auth_config['password']}"
                encoded = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
        
        # Add custom headers
        if self.headers:
            headers.update(self.headers)
        
        return headers


class APIEndpoint(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    API endpoint definition for external systems.
    
    Stores detailed information about specific API endpoints,
    their parameters, responses, and usage patterns.
    """
    
    __tablename__ = "api_endpoints"
    
    # System Reference
    system_connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("system_connections.id"),
        nullable=False,
        index=True
    )
    
    # Endpoint Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)  # GET, POST, PUT, DELETE, etc.
    
    # Documentation
    summary: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Schema Information
    request_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    response_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Configuration
    timeout_seconds: Mapped[Optional[int]] = mapped_column()
    retry_attempts: Mapped[int] = mapped_column(default=3)
    
    # Usage Statistics
    usage_count: Mapped[int] = mapped_column(default=0)
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column()
    last_used_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    system_connection: Mapped["SystemConnection"] = relationship(
        "SystemConnection",
        back_populates="api_endpoints"
    )
    data_mappings: Mapped[List["DataMapping"]] = relationship(
        "DataMapping",
        back_populates="api_endpoint",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<APIEndpoint(id={self.id}, name='{self.name}', method={self.method}, path='{self.path}')>"
    
    @property
    def full_url(self) -> str:
        """Get full URL for this endpoint."""
        base_url = self.system_connection.base_url.rstrip("/")
        path = self.path.lstrip("/")
        return f"{base_url}/{path}"
    
    def record_usage(self, response_time_ms: Optional[float] = None) -> None:
        """Record endpoint usage."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        
        if response_time_ms:
            if self.avg_response_time_ms:
                # Update running average
                self.avg_response_time_ms = (self.avg_response_time_ms + response_time_ms) / 2
            else:
                self.avg_response_time_ms = response_time_ms


class DataMapping(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    Data field mapping between systems.
    
    Stores mappings between data fields in different systems,
    including transformation rules and validation logic.
    """
    
    __tablename__ = "data_mappings"
    
    # API Endpoint Reference
    api_endpoint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("api_endpoints.id"),
        nullable=False,
        index=True
    )
    
    # Mapping Information
    source_field: Mapped[str] = mapped_column(String(255), nullable=False)
    target_field: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Data Types
    source_data_type: Mapped[Optional[str]] = mapped_column(String(100))
    target_data_type: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Transformation
    transformation_rule: Mapped[Optional[str]] = mapped_column(Text)
    transformation_code: Mapped[Optional[str]] = mapped_column(Text)
    
    # Validation
    validation_rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    is_required: Mapped[bool] = mapped_column(default=False)
    default_value: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Usage Statistics
    usage_count: Mapped[int] = mapped_column(default=0)
    success_count: Mapped[int] = mapped_column(default=0)
    error_count: Mapped[int] = mapped_column(default=0)
    
    # Relationships
    api_endpoint: Mapped["APIEndpoint"] = relationship(
        "APIEndpoint",
        back_populates="data_mappings"
    )
    
    def __repr__(self) -> str:
        return f"<DataMapping(id={self.id}, source='{self.source_field}', target='{self.target_field}')>"
    
    @property
    def success_rate(self) -> float:
        """Calculate mapping success rate."""
        if self.usage_count == 0:
            return 0.0
        return (self.success_count / self.usage_count) * 100
    
    def record_usage(self, success: bool = True) -> None:
        """Record mapping usage."""
        self.usage_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def has_transformation(self) -> bool:
        """Check if mapping has transformation logic."""
        return bool(self.transformation_rule or self.transformation_code)
    
    def needs_validation(self) -> bool:
        """Check if mapping requires validation."""
        return bool(self.validation_rules or self.is_required)
