"""
MCP (Model Context Protocol) Agent API endpoints.

These endpoints implement the conversational interface for the agentic
integration system, managing context and facilitating natural language
interaction for integration planning and deployment.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_db,
    get_ai_service,
    get_pattern_service,
    get_knowledge_graph_service
)
from app.services.ai.base import AIService, AIMessage
from app.services.knowledge.pattern_service import PatternService
from app.services.knowledge.graph_service import KnowledgeGraphService
from app.schemas.mcp import (
    ConversationStartRequest,
    ConversationResponse,
    MessageRequest,
    MessageResponse,
    ContextRetrievalRequest,
    ContextRetrievalResponse,
    IntegrationPlanningRequest,
    IntegrationPlanningResponse,
    ApprovalRequest,
    ApprovalResponse
)

router = APIRouter()

# In-memory conversation storage (in production, use Redis or database)
conversations: Dict[str, Dict[str, Any]] = {}


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def start_conversation(
    request: ConversationStartRequest,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Start a new conversational integration session.
    
    This endpoint initializes the MCP agent for a new integration
    planning session with context management.
    """
    conversation_id = str(uuid4())
    
    # Initialize conversation context
    conversations[conversation_id] = {
        "id": conversation_id,
        "user_id": request.user_id,
        "initial_request": request.initial_request,
        "context": {
            "integration_goal": request.initial_request,
            "systems_mentioned": [],
            "requirements": [],
            "modifications": [],
            "current_phase": "discovery"
        },
        "messages": [],
        "created_at": "now"
    }
    
    # Generate initial response
    initial_prompt = f"""
    You are an AI integration specialist helping a user plan a software integration.
    
    User's initial request: "{request.initial_request}"
    
    Your role is to:
    1. Understand the integration requirements
    2. Ask clarifying questions
    3. Suggest implementation approaches
    4. Help refine the integration plan
    
    Start by acknowledging their request and asking relevant clarifying questions
    to better understand their needs. Be conversational and helpful.
    """
    
    try:
        # Format messages properly for AI service
        messages = [
            AIMessage(role="system", content=initial_prompt),
            AIMessage(role="user", content=request.initial_request)
        ]

        ai_response = await ai_service.generate_response(messages)

        # Store the initial exchange
        conversations[conversation_id]["messages"] = [
            {"role": "user", "content": request.initial_request, "timestamp": "now"},
            {"role": "assistant", "content": ai_response.content, "timestamp": "now"}
        ]

        return ConversationResponse(
            conversation_id=conversation_id,
            message=ai_response.content,
            context=conversations[conversation_id]["context"],
            suggested_actions=["provide_more_details", "ask_questions", "request_examples"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation details and messages.
    """
    try:
        if conversation_id not in conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        conversation = conversations[conversation_id]
        return {
            "conversation_id": conversation_id,
            "messages": conversation.get("messages", []),
            "context": conversation.get("context", {}),
            "created_at": conversation.get("created_at"),
            "updated_at": conversation.get("updated_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: MessageRequest,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
    pattern_service: PatternService = Depends(get_pattern_service),
    kg_service: Optional[KnowledgeGraphService] = Depends(get_knowledge_graph_service)
):
    """
    Send a message in an ongoing conversation.
    
    This endpoint handles the conversational flow, maintaining context
    and providing intelligent responses based on the conversation history.
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation = conversations[conversation_id]
    
    try:
        # Add user message to conversation
        conversation["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": "now"
        })
        
        # Update context based on message
        await _update_conversation_context(conversation, request.message)
        
        # Generate contextual response
        context_prompt = f"""
        Conversation history:
        {_format_conversation_history(conversation["messages"])}
        
        Current context:
        - Integration goal: {conversation["context"]["integration_goal"]}
        - Systems mentioned: {conversation["context"]["systems_mentioned"]}
        - Current phase: {conversation["context"]["current_phase"]}
        - Requirements: {conversation["context"]["requirements"]}
        
        User's latest message: "{request.message}"
        
        Provide a helpful response that:
        1. Addresses their message directly
        2. Maintains conversation context
        3. Guides them toward a complete integration plan
        4. Asks follow-up questions if needed
        
        Be conversational and professional.
        """
        
        # Format messages properly for AI service
        messages = [
            AIMessage(role="system", content="You are an AI integration assistant helping with conversational integration planning."),
            AIMessage(role="user", content=context_prompt)
        ]
        ai_response = await ai_service.generate_response(messages)

        # Store AI response
        conversation["messages"].append({
            "role": "assistant",
            "content": ai_response.content,
            "timestamp": "now"
        })

        # Determine suggested actions based on context
        suggested_actions = _get_suggested_actions(conversation["context"])

        return MessageResponse(
            message=ai_response.content,
            context=conversation["context"],
            suggested_actions=suggested_actions,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/context", response_model=ContextRetrievalResponse)
async def retrieve_context(
    conversation_id: str,
    request: ContextRetrievalRequest,
    db: AsyncSession = Depends(get_db),
    pattern_service: PatternService = Depends(get_pattern_service)
):
    """
    Retrieve relevant context for the conversation.
    
    This endpoint implements the context retrieval phase from the sequence diagram,
    finding relevant patterns and historical integrations.
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation = conversations[conversation_id]
    
    try:
        # Search for similar patterns
        similar_patterns = []
        if request.search_patterns:
            similar_patterns = await pattern_service.find_applicable_patterns(
                db=db,
                source_system_type=request.source_system_type,
                target_system_type=request.target_system_type,
                integration_description=conversation["context"]["integration_goal"],
                limit=5
            )
        
        # Mock historical context (in production, query actual history)
        historical_context = {
            "previous_integrations": [
                {
                    "name": "Salesforce to Billing v1",
                    "success_rate": 0.95,
                    "common_issues": ["API rate limits", "Data mapping complexity"]
                }
            ],
            "system_capabilities": {
                "salesforce": {
                    "api_version": "v54.0",
                    "supported_objects": ["Account", "Contact", "Opportunity"],
                    "rate_limits": "100 calls/second"
                }
            }
        }
        
        return ContextRetrievalResponse(
            conversation_id=conversation_id,
            similar_patterns=similar_patterns,
            historical_context=historical_context,
            system_capabilities=historical_context["system_capabilities"],
            recommendations=[
                "Consider using bulk API for large data volumes",
                "Implement exponential backoff for rate limiting",
                "Use webhook notifications for real-time sync"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/plan", response_model=IntegrationPlanningResponse)
async def generate_integration_plan(
    conversation_id: str,
    request: IntegrationPlanningRequest,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Generate a comprehensive integration plan based on the conversation.
    
    This endpoint creates the detailed integration plan that the user
    can review, modify, and approve for deployment.
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation = conversations[conversation_id]
    
    try:
        # Generate comprehensive plan
        planning_prompt = f"""
        Based on this conversation, create a detailed integration plan:
        
        Integration Goal: {conversation["context"]["integration_goal"]}
        Systems: {conversation["context"]["systems_mentioned"]}
        Requirements: {conversation["context"]["requirements"]}
        Modifications: {conversation["context"]["modifications"]}
        
        Conversation Summary:
        {_format_conversation_history(conversation["messages"][-6:])}  # Last 6 messages
        
        Create a comprehensive plan including:
        1. Executive Summary
        2. Technical Architecture
        3. Data Flow Diagram (text description)
        4. Implementation Steps
        5. Testing Strategy
        6. Deployment Plan
        7. Risk Assessment
        8. Timeline Estimate
        
        Format as structured JSON with clear sections.
        """
        
        # Format messages properly for AI service
        messages = [
            AIMessage(role="system", content="You are an AI integration planning specialist. Create detailed, structured integration plans."),
            AIMessage(role="user", content=planning_prompt)
        ]
        plan = await ai_service.generate_response(messages)
        
        # Update conversation context
        conversation["context"]["current_phase"] = "planning"
        conversation["context"]["plan_generated"] = True
        
        return IntegrationPlanningResponse(
            conversation_id=conversation_id,
            integration_plan=plan.content,
            estimated_timeline="2-3 weeks",
            complexity_score=7,
            confidence_level=0.85,
            next_steps=[
                "Review the proposed plan",
                "Request modifications if needed",
                "Approve for implementation",
                "Schedule deployment"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/approve", response_model=ApprovalResponse)
async def approve_integration(
    conversation_id: str,
    request: ApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve an integration plan for deployment.
    
    This endpoint handles the final approval phase, transitioning
    from planning to implementation.
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation = conversations[conversation_id]
    
    try:
        if request.approved:
            # Update conversation status
            conversation["context"]["current_phase"] = "approved"
            conversation["context"]["approved_at"] = "now"
            conversation["context"]["approval_notes"] = request.notes
            
            # In production, this would trigger actual deployment
            deployment_id = str(uuid4())
            
            return ApprovalResponse(
                conversation_id=conversation_id,
                approved=True,
                deployment_id=deployment_id,
                status="approved_for_deployment",
                message="Integration approved and queued for deployment",
                estimated_deployment_time="30 minutes"
            )
        else:
            # Handle rejection
            conversation["context"]["current_phase"] = "revision_needed"
            conversation["context"]["rejection_notes"] = request.notes
            
            return ApprovalResponse(
                conversation_id=conversation_id,
                approved=False,
                status="revision_needed",
                message="Integration plan needs revision based on feedback",
                revision_suggestions=[
                    "Address the concerns mentioned in notes",
                    "Modify the technical approach",
                    "Update timeline estimates"
                ]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}"
        )


# Duplicate endpoint removed - using the first one above


# Helper functions
async def _update_conversation_context(conversation: Dict[str, Any], message: str):
    """Update conversation context based on new message."""
    context = conversation["context"]
    
    # Simple keyword extraction (in production, use NLP)
    message_lower = message.lower()
    
    # Extract system mentions
    systems = ["salesforce", "billing", "erp", "crm", "database", "api"]
    for system in systems:
        if system in message_lower and system not in context["systems_mentioned"]:
            context["systems_mentioned"].append(system)
    
    # Extract requirements
    requirement_keywords = ["need", "require", "must", "should", "want"]
    if any(keyword in message_lower for keyword in requirement_keywords):
        context["requirements"].append(message)
    
    # Track modifications
    modification_keywords = ["modify", "change", "update", "add", "include"]
    if any(keyword in message_lower for keyword in modification_keywords):
        context["modifications"].append(message)


def _format_conversation_history(messages: List[Dict[str, Any]]) -> str:
    """Format conversation history for AI context."""
    formatted = []
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted.append(f"{role}: {msg['content']}")
    return "\n".join(formatted)


def _get_suggested_actions(context: Dict[str, Any]) -> List[str]:
    """Get suggested actions based on conversation context."""
    phase = context.get("current_phase", "discovery")
    
    if phase == "discovery":
        return ["provide_system_details", "clarify_requirements", "ask_questions"]
    elif phase == "planning":
        return ["review_plan", "request_modifications", "approve_plan"]
    elif phase == "approved":
        return ["monitor_deployment", "view_logs", "test_integration"]
    else:
        return ["continue_conversation", "ask_questions", "provide_feedback"]
