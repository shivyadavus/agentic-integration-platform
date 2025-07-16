"""
Integration Tests for Agentic Workflow
Tests the complete sequence: User → MCP Agent → Knowledge Graph → External APIs → Context Store
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.ai.factory import AIServiceFactory
from app.services.knowledge.graph_service import GraphService
from app.services.knowledge.vector_service import VectorService


class TestAgenticWorkflowIntegration:
    """Test the complete agentic integration workflow"""
    
    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service to return predictable responses"""
        with patch.object(AIServiceFactory, 'create_service') as mock:
            ai_service = AsyncMock()
            ai_service.generate_response.return_value = {
                "content": "I'll help you connect Salesforce to your billing system. Let me analyze the requirements and create an integration plan.",
                "context": {"systems": ["salesforce", "billing"], "intent": "integration"},
                "suggested_actions": ["Review data mapping", "Configure sync frequency", "Test connection"]
            }
            mock.return_value = ai_service
            yield ai_service
    
    @pytest.fixture
    def mock_knowledge_services(self):
        """Mock knowledge graph and vector services"""
        with patch.object(GraphService, 'search_patterns') as mock_graph, \
             patch.object(VectorService, 'semantic_search') as mock_vector:
            
            mock_graph.return_value = {
                "patterns": [
                    {
                        "id": "sf-billing-pattern-1",
                        "name": "Salesforce to Billing Integration",
                        "description": "Standard pattern for syncing SF data to billing systems",
                        "field_mappings": {"Account.Id": "customer_id", "Opportunity.Amount": "invoice_amount"}
                    }
                ],
                "total_found": 1
            }
            
            mock_vector.return_value = {
                "results": [
                    {
                        "id": "semantic-1",
                        "content": "Salesforce billing integration best practices",
                        "score": 0.95,
                        "metadata": {"type": "integration_pattern"}
                    }
                ],
                "total_found": 1
            }
            
            yield mock_graph, mock_vector

    async def test_complete_salesforce_billing_workflow(self, client, mock_ai_service, mock_knowledge_services):
        """Test the complete workflow from initial request to deployment"""
        
        # Step 1: Start conversation with initial request
        response = await client.post("/api/v1/mcp/conversations", json={
            "initial_request": "Connect Salesforce to our billing system"
        })
        assert response.status_code == 200
        conversation_data = response.json()
        conversation_id = conversation_data["conversation_id"]
        
        # Verify initial response contains relevant information
        assert "salesforce" in conversation_data["message"].lower()
        assert "billing" in conversation_data["message"].lower()
        assert len(conversation_data["suggested_actions"]) > 0
        
        # Step 2: Retrieve context (simulates MCP Agent querying Context Store)
        context_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/context", json={
            "source_system_type": "salesforce",
            "target_system_type": "billing",
            "search_patterns": True
        })
        assert context_response.status_code == 200
        context_data = context_response.json()
        
        # Verify context includes historical patterns
        assert "patterns" in context_data
        assert len(context_data["patterns"]) > 0
        
        # Step 3: Generate initial integration plan
        plan_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/plan", json={
            "include_testing": True,
            "include_deployment": True,
            "detail_level": "comprehensive"
        })
        assert plan_response.status_code == 200
        plan_data = plan_response.json()
        
        # Verify plan contains essential elements
        assert "integration_plan" in plan_data
        assert "field_mappings" in plan_data
        assert "testing_strategy" in plan_data
        
        # Step 4: Send modification request
        modification_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/messages", json={
            "message": "Modify to include tax calculations"
        })
        assert modification_response.status_code == 200
        modification_data = modification_response.json()
        
        # Verify modification is acknowledged
        assert "tax" in modification_data["message"].lower()
        assert "calculation" in modification_data["message"].lower()
        
        # Step 5: Generate updated plan with tax calculations
        updated_plan_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/plan", json={
            "include_testing": True,
            "include_deployment": True,
            "detail_level": "comprehensive",
            "modifications": ["include tax calculations"]
        })
        assert updated_plan_response.status_code == 200
        updated_plan_data = updated_plan_response.json()
        
        # Verify updated plan includes tax logic
        plan_content = str(updated_plan_data)
        assert "tax" in plan_content.lower()
        
        # Step 6: Approve and deploy
        approval_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/approve", json={
            "approved": True,
            "notes": "Approved for deployment with tax calculations"
        })
        assert approval_response.status_code == 200
        approval_data = approval_response.json()
        
        # Verify deployment is initiated
        assert approval_data["status"] in ["approved", "deploying", "deployed"]
        
        # Step 7: Verify integration is created
        integrations_response = await client.get("/api/v1/integrations/")
        assert integrations_response.status_code == 200
        integrations = integrations_response.json()
        
        # Find the created integration
        salesforce_integration = None
        for integration in integrations:
            if "salesforce" in integration["name"].lower() and "billing" in integration["name"].lower():
                salesforce_integration = integration
                break
        
        assert salesforce_integration is not None
        assert salesforce_integration["status"] in ["draft", "active", "deploying"]

    async def test_knowledge_graph_integration(self, client, mock_knowledge_services):
        """Test Knowledge Graph queries during workflow"""
        
        # Test pattern search
        pattern_response = await client.post("/api/v1/knowledge/patterns/search", json={
            "description": "Salesforce billing integration",
            "source_system_type": "salesforce",
            "target_system_type": "billing"
        })
        assert pattern_response.status_code == 200
        pattern_data = pattern_response.json()
        
        assert "patterns" in pattern_data
        assert len(pattern_data["patterns"]) > 0
        assert pattern_data["patterns"][0]["name"] == "Salesforce to Billing Integration"
        
        # Test semantic search
        semantic_response = await client.post("/api/v1/knowledge/semantic/search", json={
            "query": "Salesforce billing integration tax calculations",
            "limit": 5
        })
        assert semantic_response.status_code == 200
        semantic_data = semantic_response.json()
        
        assert "results" in semantic_data
        assert len(semantic_data["results"]) > 0
        assert semantic_data["results"][0]["score"] > 0.8

    async def test_external_api_connectivity_simulation(self, client):
        """Test external API connectivity checks"""
        
        # Create an integration to test API connectivity
        integration_response = await client.post("/api/v1/integrations/", json={
            "name": "Salesforce API Test",
            "natural_language_spec": "Test Salesforce API connectivity for billing integration"
        })
        assert integration_response.status_code == 200
        integration = integration_response.json()
        integration_id = integration["id"]
        
        # Generate plan (which should include API testing)
        plan_response = await client.post(f"/api/v1/integrations/{integration_id}/plan", json={
            "source_system_type": "salesforce",
            "target_system_type": "billing",
            "estimated_complexity": "medium"
        })
        assert plan_response.status_code == 200
        plan_data = plan_response.json()
        
        # Verify plan includes API connectivity information
        assert "api" in str(plan_data).lower()
        assert "connectivity" in str(plan_data).lower() or "connection" in str(plan_data).lower()

    async def test_context_store_persistence(self, client, mock_ai_service):
        """Test that context is properly stored and retrieved"""
        
        # Start conversation
        response = await client.post("/api/v1/mcp/conversations", json={
            "initial_request": "Connect Salesforce to billing system"
        })
        conversation_id = response.json()["conversation_id"]
        
        # Send multiple messages to build context
        messages = [
            "Make it sync only successful payments",
            "Add currency conversion",
            "Include refund handling"
        ]
        
        for message in messages:
            await client.post(f"/api/v1/mcp/conversations/{conversation_id}/messages", json={
                "message": message
            })
        
        # Retrieve conversation to verify context persistence
        conversation_response = await client.get(f"/api/v1/mcp/conversations/{conversation_id}")
        assert conversation_response.status_code == 200
        conversation_data = conversation_response.json()
        
        # Verify all messages are stored
        assert len(conversation_data.get("messages", [])) >= len(messages)
        
        # Verify context includes all modifications
        context_str = str(conversation_data).lower()
        assert "successful payments" in context_str
        assert "currency conversion" in context_str
        assert "refund handling" in context_str

    async def test_error_handling_unknown_system(self, client, mock_ai_service):
        """Test error handling for unknown systems"""
        
        # Mock AI service to return error response for unknown system
        mock_ai_service.generate_response.return_value = {
            "content": "I don't recognize 'UnknownSystem'. Could you clarify which system you're referring to? Here are some similar systems I know about: Salesforce, HubSpot, Stripe.",
            "context": {"error": "unknown_system", "suggestions": ["salesforce", "hubspot", "stripe"]},
            "suggested_actions": ["Clarify system name", "Choose from suggestions"]
        }
        
        response = await client.post("/api/v1/mcp/conversations", json={
            "initial_request": "Connect UnknownSystem to our billing system"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify error is handled gracefully
        assert "don't recognize" in data["message"] or "unknown" in data["message"].lower()
        assert len(data["suggested_actions"]) > 0

    async def test_iterative_refinement_workflow(self, client, mock_ai_service):
        """Test iterative refinement of integration requirements"""
        
        # Start with basic request
        response = await client.post("/api/v1/mcp/conversations", json={
            "initial_request": "Connect Stripe to QuickBooks"
        })
        conversation_id = response.json()["conversation_id"]
        
        # Apply multiple refinements
        refinements = [
            "Actually, make it sync only successful payments",
            "Add currency conversion for international payments", 
            "Include refund handling",
            "Add webhook notifications for real-time updates"
        ]
        
        for refinement in refinements:
            refinement_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/messages", json={
                "message": refinement
            })
            assert refinement_response.status_code == 200
        
        # Generate final plan
        final_plan_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/plan", json={
            "include_testing": True,
            "include_deployment": True
        })
        assert final_plan_response.status_code == 200
        
        # Verify final plan incorporates all refinements
        plan_content = str(final_plan_response.json()).lower()
        assert "successful payments" in plan_content
        assert "currency conversion" in plan_content
        assert "refund" in plan_content
        assert "webhook" in plan_content

    async def test_deployment_workflow(self, client):
        """Test the deployment process"""
        
        # Create integration
        integration_response = await client.post("/api/v1/integrations/", json={
            "name": "Test Deployment Integration",
            "natural_language_spec": "Test integration for deployment workflow"
        })
        integration_id = integration_response.json()["id"]
        
        # Deploy integration
        deploy_response = await client.post(f"/api/v1/integrations/{integration_id}/deploy", json={
            "environment": "staging",
            "auto_approve": True
        })
        assert deploy_response.status_code == 200
        deploy_data = deploy_response.json()
        
        # Verify deployment response
        assert deploy_data["status"] in ["deploying", "deployed", "active"]
        assert deploy_data["environment"] == "staging"
        
        # Verify integration status is updated
        updated_integration_response = await client.get(f"/api/v1/integrations/{integration_id}")
        assert updated_integration_response.status_code == 200
        updated_integration = updated_integration_response.json()
        
        assert updated_integration["status"] in ["deploying", "deployed", "active"]


@pytest.mark.asyncio
class TestWorkflowPerformance:
    """Performance tests for the agentic workflow"""
    
    async def test_response_time_benchmarks(self, client):
        """Test that workflow steps complete within acceptable time limits"""
        import time
        
        # Test conversation start time
        start_time = time.time()
        response = await client.post("/api/v1/mcp/conversations", json={
            "initial_request": "Connect Salesforce to billing system"
        })
        conversation_time = time.time() - start_time
        
        assert response.status_code == 200
        assert conversation_time < 5.0  # Should complete within 5 seconds
        
        conversation_id = response.json()["conversation_id"]
        
        # Test plan generation time
        start_time = time.time()
        plan_response = await client.post(f"/api/v1/mcp/conversations/{conversation_id}/plan", json={
            "include_testing": True,
            "include_deployment": True
        })
        plan_time = time.time() - start_time
        
        assert plan_response.status_code == 200
        assert plan_time < 10.0  # Should complete within 10 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
