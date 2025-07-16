"""
Pydantic schemas for MCP (Model Context Protocol) API endpoints.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationStartRequest(BaseModel):
    """Schema for starting a new conversation."""
    initial_request: str = Field(
        ...,
        description="Initial integration request from user",
        example="Connect Salesforce to our billing system"
    )
    user_id: Optional[str] = Field(
        None,
        description="User identifier for context",
        example="user_123"
    )


class ConversationResponse(BaseModel):
    """Schema for conversation start response."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    message: str = Field(..., description="AI agent's response message")
    context: Dict[str, Any] = Field(..., description="Current conversation context")
    suggested_actions: List[str] = Field(
        default_factory=list,
        description="Suggested next actions for the user"
    )


class MessageRequest(BaseModel):
    """Schema for sending a message in conversation."""
    message: str = Field(
        ...,
        description="User's message",
        example="Modify to include tax calculations"
    )


class MessageResponse(BaseModel):
    """Schema for message response."""
    message: str = Field(..., description="AI agent's response")
    context: Dict[str, Any] = Field(..., description="Updated conversation context")
    suggested_actions: List[str] = Field(
        default_factory=list,
        description="Suggested next actions"
    )
    conversation_id: str = Field(..., description="Conversation identifier")


class ContextRetrievalRequest(BaseModel):
    """Schema for context retrieval request."""
    source_system_type: Optional[str] = Field(
        None,
        description="Source system type for pattern matching",
        example="salesforce"
    )
    target_system_type: Optional[str] = Field(
        None,
        description="Target system type for pattern matching",
        example="billing_system"
    )
    search_patterns: bool = Field(
        default=True,
        description="Whether to search for similar patterns"
    )


class ContextRetrievalResponse(BaseModel):
    """Schema for context retrieval response."""
    conversation_id: str = Field(..., description="Conversation identifier")
    similar_patterns: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Similar integration patterns found"
    )
    historical_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Historical integration context"
    )
    system_capabilities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Capabilities of involved systems"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="AI recommendations based on context"
    )


class IntegrationPlanningRequest(BaseModel):
    """Schema for integration planning request."""
    include_testing: bool = Field(
        default=True,
        description="Include testing strategy in plan"
    )
    include_deployment: bool = Field(
        default=True,
        description="Include deployment strategy in plan"
    )
    detail_level: str = Field(
        default="comprehensive",
        description="Level of detail for the plan",
        example="comprehensive"
    )


class IntegrationPlanningResponse(BaseModel):
    """Schema for integration planning response."""
    conversation_id: str = Field(..., description="Conversation identifier")
    integration_plan: str = Field(..., description="Detailed integration plan")
    estimated_timeline: str = Field(..., description="Estimated implementation timeline")
    complexity_score: int = Field(
        ...,
        description="Complexity score from 1-10",
        ge=1,
        le=10
    )
    confidence_level: float = Field(
        ...,
        description="AI confidence in the plan",
        ge=0.0,
        le=1.0
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps"
    )


class ApprovalRequest(BaseModel):
    """Schema for integration approval request."""
    approved: bool = Field(..., description="Whether the integration is approved")
    notes: Optional[str] = Field(
        None,
        description="Approval or rejection notes",
        example="Looks good, please proceed with deployment"
    )
    modifications_requested: Optional[List[str]] = Field(
        default_factory=list,
        description="Specific modifications requested if not approved"
    )


class ApprovalResponse(BaseModel):
    """Schema for approval response."""
    conversation_id: str = Field(..., description="Conversation identifier")
    approved: bool = Field(..., description="Whether approved")
    deployment_id: Optional[str] = Field(None, description="Deployment ID if approved")
    status: str = Field(..., description="Current status")
    message: str = Field(..., description="Status message")
    estimated_deployment_time: Optional[str] = Field(
        None,
        description="Estimated deployment time if approved"
    )
    revision_suggestions: Optional[List[str]] = Field(
        default_factory=list,
        description="Suggestions for revision if not approved"
    )
