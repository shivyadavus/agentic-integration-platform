"""
Knowledge graph domain models for the agentic integration platform.

This module defines models for storing and managing knowledge graph entities,
relationships, patterns, and semantic mappings used by the AI system.
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin, AuditMixin, MetadataMixin


class EntityType(enum.Enum):
    """Types of entities in the knowledge graph."""
    
    BUSINESS_OBJECT = "business_object"    # Customer, Order, Product, etc.
    API_ENDPOINT = "api_endpoint"          # REST endpoints, GraphQL queries
    DATA_FIELD = "data_field"              # Individual data fields/properties
    SYSTEM = "system"                      # External systems (CRM, ERP, etc.)
    PROCESS = "process"                    # Business processes
    RULE = "rule"                          # Business rules and constraints
    PATTERN = "pattern"                    # Integration patterns
    TRANSFORMATION = "transformation"       # Data transformation logic


class RelationshipType(enum.Enum):
    """Types of relationships between entities."""
    
    # Data relationships
    HAS_FIELD = "has_field"                # Entity has a data field
    MAPS_TO = "maps_to"                    # Field maps to another field
    TRANSFORMS_TO = "transforms_to"        # Data transformation relationship
    
    # System relationships
    BELONGS_TO = "belongs_to"              # Entity belongs to system
    CONNECTS_TO = "connects_to"            # System connects to system
    DEPENDS_ON = "depends_on"              # Dependency relationship
    
    # Process relationships
    TRIGGERS = "triggers"                  # Event triggers process
    PART_OF = "part_of"                    # Entity is part of process
    FOLLOWS = "follows"                    # Sequential relationship
    
    # Semantic relationships
    SIMILAR_TO = "similar_to"              # Semantic similarity
    EQUIVALENT_TO = "equivalent_to"        # Semantic equivalence
    INHERITS_FROM = "inherits_from"        # Inheritance relationship


class Entity(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    Knowledge graph entity representing business objects, systems, or concepts.
    
    Entities are the nodes in our knowledge graph, representing everything from
    business objects like customers and orders to technical concepts like APIs
    and data transformations.
    """
    
    __tablename__ = "kg_entities"
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType),
        nullable=False,
        index=True
    )
    
    # Semantic Information
    semantic_label: Mapped[Optional[str]] = mapped_column(String(255))
    canonical_name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    aliases: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Schema Information
    schema_definition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    data_type: Mapped[Optional[str]] = mapped_column(String(100))
    constraints: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # System Context
    system_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("system_connections.id"),
        index=True
    )
    api_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Vector Embeddings
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Usage Statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Confidence and Quality
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    outgoing_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan"
    )
    incoming_relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.target_entity_id", 
        back_populates="target_entity"
    )
    
    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name='{self.name}', type={self.entity_type.value})>"
    
    def get_aliases(self) -> List[str]:
        """Get entity aliases as list."""
        return self.aliases or []
    
    def add_alias(self, alias: str) -> None:
        """Add an alias to the entity."""
        current_aliases = self.get_aliases()
        if alias not in current_aliases:
            current_aliases.append(alias)
            self.aliases = current_aliases
    
    def get_related_entities(self, relationship_type: Optional[RelationshipType] = None) -> List["Entity"]:
        """Get entities related to this entity."""
        related = []
        for rel in self.outgoing_relationships:
            if relationship_type is None or rel.relationship_type == relationship_type:
                related.append(rel.target_entity)
        return related
    
    def update_usage(self) -> None:
        """Update usage statistics."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()


class Relationship(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    Knowledge graph relationship connecting two entities.
    
    Relationships are the edges in our knowledge graph, representing semantic
    connections, data mappings, and business logic between entities.
    """
    
    __tablename__ = "kg_relationships"
    
    # Entity References
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kg_entities.id"),
        nullable=False,
        index=True
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kg_entities.id"),
        nullable=False,
        index=True
    )
    
    # Relationship Information
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType),
        nullable=False,
        index=True
    )
    
    # Semantic Information
    label: Mapped[Optional[str]] = mapped_column(String(255))
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Transformation Logic
    transformation_rule: Mapped[Optional[str]] = mapped_column(Text)
    transformation_code: Mapped[Optional[str]] = mapped_column(Text)
    
    # Quality and Confidence
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    strength: Mapped[float] = mapped_column(Float, default=1.0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Usage Statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    source_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
        back_populates="outgoing_relationships"
    )
    target_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
        back_populates="incoming_relationships"
    )
    
    def __repr__(self) -> str:
        return f"<Relationship(id={self.id}, type={self.relationship_type.value}, strength={self.strength})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of this relationship."""
        if self.usage_count == 0:
            return 0.0
        return (self.success_count / self.usage_count) * 100
    
    def record_usage(self, success: bool = True) -> None:
        """Record usage of this relationship."""
        self.usage_count += 1
        if success:
            self.success_count += 1


class Pattern(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    Integration pattern learned from successful integrations.
    
    Patterns capture reusable integration logic, data transformations,
    and business rules that can be applied to similar integration scenarios.
    """
    
    __tablename__ = "kg_patterns"
    
    # Pattern Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pattern_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Pattern Definition
    pattern_definition: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    code_template: Mapped[Optional[str]] = mapped_column(Text)
    
    # Applicability
    source_system_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    target_system_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    use_cases: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Quality Metrics
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Learning Information
    learned_from_integration_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("integrations.id")
    )
    
    def __repr__(self) -> str:
        return f"<Pattern(id={self.id}, name='{self.name}', type='{self.pattern_type}')>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of this pattern."""
        if self.usage_count == 0:
            return 0.0
        return (self.success_count / self.usage_count) * 100
    
    def is_applicable_to(self, source_type: str, target_type: str) -> bool:
        """Check if pattern is applicable to given system types."""
        source_match = (
            not self.source_system_types or 
            source_type in self.source_system_types
        )
        target_match = (
            not self.target_system_types or 
            target_type in self.target_system_types
        )
        return source_match and target_match
