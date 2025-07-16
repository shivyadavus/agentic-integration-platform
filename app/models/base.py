"""
Base model classes and mixins for the agentic integration platform.

This module provides foundational database model classes with common functionality
like timestamps, UUIDs, and audit trails.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class BaseModel(Base):
    """
    Base model class with common fields and functionality.
    
    Provides UUID primary key, creation/update timestamps, and common methods
    for all domain models.
    """
    
    __abstract__ = True
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary."""
        # Filter out keys that don't correspond to model columns
        valid_keys = {column.name for column in cls.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


class TimestampMixin:
    """Mixin to add creation and update timestamps to models."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )


class AuditMixin:
    """Mixin to add audit trail fields to models."""
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    version: Mapped[int] = mapped_column(
        default=1,
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin to add soft delete functionality to models."""
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None
    
    def soft_delete(self, deleted_by: Optional[uuid.UUID] = None) -> None:
        """Soft delete the record."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by
    
    def restore(self) -> None:
        """Restore a soft deleted record."""
        self.deleted_at = None
        self.deleted_by = None


class MetadataMixin:
    """Mixin to add metadata fields to models."""
    
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata_",
        Text,
        nullable=True
    )
    
    tags: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as dictionary."""
        if self.metadata_:
            import json
            try:
                return json.loads(self.metadata_)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in metadata for {self.__class__.__name__} {self.id}")
                return {}
        return {}
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set metadata from dictionary."""
        import json
        self.metadata_ = json.dumps(metadata)
    
    def get_tags(self) -> list[str]:
        """Get tags as list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
        return []
    
    def set_tags(self, tags: list[str]) -> None:
        """Set tags from list."""
        self.tags = ",".join(tags) if tags else None
    
    def add_tag(self, tag: str) -> None:
        """Add a single tag."""
        current_tags = self.get_tags()
        if tag not in current_tags:
            current_tags.append(tag)
            self.set_tags(current_tags)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a single tag."""
        current_tags = self.get_tags()
        if tag in current_tags:
            current_tags.remove(tag)
            self.set_tags(current_tags)
