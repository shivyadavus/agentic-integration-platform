"""
Simple test API endpoints to verify the system is working.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify API is working."""
    return {
        "message": "API is working!",
        "status": "success",
        "endpoints_available": [
            "/api/v1/integrations/",
            "/api/v1/knowledge/",
            "/api/v1/mcp/"
        ]
    }


@router.post("/test/integration")
async def test_integration_creation():
    """Test endpoint for integration creation flow."""
    return {
        "message": "Integration creation endpoint is working!",
        "flow": [
            "1. User provides natural language spec",
            "2. AI analyzes and generates plan", 
            "3. System finds similar patterns",
            "4. User reviews and approves",
            "5. Integration is deployed"
        ],
        "example_request": {
            "name": "Salesforce to Billing Integration",
            "natural_language_spec": "Connect Salesforce to our billing system and sync customer data when accounts are created",
            "integration_type": "api"
        }
    }


@router.get("/test/mcp")
async def test_mcp_conversation():
    """Test endpoint for MCP conversation flow."""
    return {
        "message": "MCP conversation endpoint is working!",
        "conversation_flow": [
            "1. Start conversation with initial request",
            "2. AI asks clarifying questions",
            "3. Context retrieval from knowledge base",
            "4. Generate integration plan",
            "5. User approval and deployment"
        ],
        "example_conversation": {
            "user": "Connect Salesforce to our billing system",
            "assistant": "I can help you create that integration. Can you tell me more about what specific data you want to sync and when?"
        }
    }


@router.get("/test/knowledge")
async def test_knowledge_search():
    """Test endpoint for knowledge graph search."""
    return {
        "message": "Knowledge graph search is working!",
        "search_capabilities": [
            "Pattern similarity search",
            "System schema queries", 
            "Semantic search across entities",
            "Relationship mapping"
        ],
        "example_patterns": [
            {
                "name": "CRM to Billing Sync",
                "success_rate": 0.95,
                "systems": ["salesforce", "billing_system"]
            },
            {
                "name": "Real-time Customer Updates",
                "success_rate": 0.88,
                "systems": ["crm", "erp"]
            }
        ]
    }
