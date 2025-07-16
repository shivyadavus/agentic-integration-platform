"""
Pydantic schemas for knowledge graph API endpoints.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PatternSearchRequest(BaseModel):
    """Schema for pattern search requests."""
    description: str = Field(
        ..., 
        description="Natural language description of the integration need",
        example="Sync customer data from CRM to billing system"
    )
    source_system_type: Optional[str] = Field(
        None,
        description="Type of source system",
        example="salesforce"
    )
    target_system_type: Optional[str] = Field(
        None,
        description="Type of target system", 
        example="billing_system"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of patterns to return",
        ge=1,
        le=100
    )


class PatternSearchResponse(BaseModel):
    """Schema for pattern search responses."""
    query: str = Field(..., description="Original search query")
    patterns: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Found patterns with similarity scores"
    )
    total_found: int = Field(..., description="Total number of patterns found")


class SchemaQueryRequest(BaseModel):
    """Schema for system schema queries."""
    system_type: Optional[str] = Field(
        None,
        description="Type of system to query schemas for",
        example="salesforce"
    )
    schema_name: Optional[str] = Field(
        None,
        description="Specific schema name to search for",
        example="Account"
    )
    limit: int = Field(
        default=50,
        description="Maximum number of schemas to return",
        ge=1,
        le=200
    )


class SchemaQueryResponse(BaseModel):
    """Schema for system schema query responses."""
    system_type: Optional[str] = Field(None, description="Queried system type")
    schemas: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Found system schemas"
    )
    mappings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Related data mappings"
    )
    total_found: int = Field(..., description="Total number of schemas found")


class SemanticSearchRequest(BaseModel):
    """Schema for semantic search requests."""
    query: str = Field(
        ...,
        description="Natural language query",
        example="How to handle customer data synchronization with error handling?"
    )
    limit: int = Field(
        default=20,
        description="Maximum number of results to return",
        ge=1,
        le=100
    )
    min_similarity_score: float = Field(
        default=0.7,
        description="Minimum similarity score for results",
        ge=0.0,
        le=1.0
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional filters for the search"
    )


class SemanticSearchResponse(BaseModel):
    """Schema for semantic search responses."""
    query: str = Field(..., description="Original search query")
    results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Search results with similarity scores"
    )
    total_found: int = Field(..., description="Total number of results found")


class EntityCreateRequest(BaseModel):
    """Schema for creating knowledge graph entities."""
    entity_type: str = Field(
        ...,
        description="Type of entity to create",
        example="system"
    )
    properties: Dict[str, Any] = Field(
        ...,
        description="Entity properties",
        example={
            "name": "Salesforce CRM",
            "type": "crm",
            "api_version": "v54.0",
            "description": "Customer relationship management system"
        }
    )


class EntityResponse(BaseModel):
    """Schema for entity responses."""
    id: str = Field(..., description="Entity ID")
    entity_type: str = Field(..., description="Entity type")
    properties: Dict[str, Any] = Field(..., description="Entity properties")


class RelationshipCreateRequest(BaseModel):
    """Schema for creating relationships between entities."""
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(
        ...,
        description="Type of relationship",
        example="INTEGRATES_WITH"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Relationship properties"
    )


class RelationshipResponse(BaseModel):
    """Schema for relationship responses."""
    id: str = Field(..., description="Relationship ID")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(..., description="Relationship type")
    properties: Dict[str, Any] = Field(..., description="Relationship properties")
