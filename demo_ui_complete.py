#!/usr/bin/env python3
"""
Complete UI Demo Script for Agentic Integration Platform

This script demonstrates the full functionality of the modern UI
by creating sample data and testing all major features.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
import random

# API Base URL
API_BASE = "http://localhost:8000/api/v1"
UI_URL = "http://localhost:3000"

class AgenticPlatformDemo:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def create_sample_integrations(self):
        """Create sample integrations to populate the dashboard"""
        print("🚀 Creating sample integrations...")
        
        sample_integrations = [
            {
                "name": "Salesforce to QuickBooks Sync",
                "natural_language_spec": "Automatically sync customer data from Salesforce to QuickBooks, including contact information, billing addresses, and payment terms. Handle duplicate detection and data validation.",
                "integration_type": "sync",
                "status": "active"
            },
            {
                "name": "Stripe Payment Webhooks",
                "natural_language_spec": "Process Stripe payment webhooks to update order status in our e-commerce system. Handle successful payments, failed payments, and refunds with proper error handling.",
                "integration_type": "webhook",
                "status": "generating"
            },
            {
                "name": "HubSpot Lead Processing",
                "natural_language_spec": "Automatically process new leads from HubSpot, score them based on company size and industry, and route high-value leads to senior sales reps via Slack notifications.",
                "integration_type": "async",
                "status": "draft"
            },
            {
                "name": "Multi-Currency Invoice System",
                "natural_language_spec": "Create invoices in multiple currencies with real-time exchange rates, automatic tax calculations based on customer location, and dunning processes for overdue payments.",
                "integration_type": "sync",
                "status": "ready"
            },
            {
                "name": "Inventory Management Sync",
                "natural_language_spec": "Synchronize inventory levels between Shopify, Amazon, and internal warehouse management system. Handle stock alerts and automatic reordering.",
                "integration_type": "sync",
                "status": "error"
            }
        ]
        
        created_integrations = []
        for integration in sample_integrations:
            try:
                async with self.session.post(f"{API_BASE}/integrations/", json=integration) as response:
                    if response.status == 201:
                        result = await response.json()
                        created_integrations.append(result)
                        print(f"✅ Created: {integration['name']}")
                    else:
                        print(f"❌ Failed to create: {integration['name']} - Status: {response.status}")
            except Exception as e:
                print(f"❌ Error creating {integration['name']}: {e}")
                
        return created_integrations

    async def create_sample_conversations(self):
        """Create sample MCP conversations"""
        print("💬 Creating sample MCP conversations...")
        
        conversations = [
            {
                "title": "Salesforce Integration Help",
                "messages": [
                    {
                        "role": "user",
                        "content": "I need help creating a Salesforce to billing system integration with multi-currency support"
                    },
                    {
                        "role": "assistant", 
                        "content": "I'd be happy to help you create a Salesforce to billing system integration with multi-currency support! This is a common integration pattern that involves several key components:\n\n**Key Requirements:**\n1. **Data Synchronization**: Customer data, products, and pricing\n2. **Currency Handling**: Real-time exchange rates and conversion\n3. **Tax Calculations**: Location-based tax rules\n4. **Invoice Generation**: Automated billing workflows\n\nWould you like me to start by analyzing your current Salesforce setup and billing system requirements?"
                    }
                ]
            },
            {
                "title": "Webhook Integration Patterns",
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the best practices for handling webhook integrations?"
                    },
                    {
                        "role": "assistant",
                        "content": "Great question! Here are the key best practices for webhook integrations:\n\n**Security & Reliability:**\n- Always verify webhook signatures\n- Implement idempotency to handle duplicate events\n- Use HTTPS endpoints with proper SSL certificates\n- Set up proper authentication and authorization\n\n**Error Handling:**\n- Implement exponential backoff for retries\n- Use dead letter queues for failed events\n- Log all webhook events for debugging\n- Return appropriate HTTP status codes\n\n**Performance:**\n- Process webhooks asynchronously when possible\n- Implement rate limiting and throttling\n- Use queuing systems for high-volume events\n\nWould you like me to help you implement any of these patterns for your specific use case?"
                    }
                ]
            }
        ]
        
        created_conversations = []
        for conv_data in conversations:
            try:
                # Create conversation
                async with self.session.post(f"{API_BASE}/mcp/conversations", 
                                           json={"title": conv_data["title"]}) as response:
                    if response.status == 201:
                        conversation = await response.json()
                        
                        # Add messages
                        for message in conv_data["messages"]:
                            async with self.session.post(
                                f"{API_BASE}/mcp/conversations/{conversation['id']}/messages",
                                json=message
                            ) as msg_response:
                                if msg_response.status == 200:
                                    print(f"✅ Added message to: {conv_data['title']}")
                        
                        created_conversations.append(conversation)
                        print(f"✅ Created conversation: {conv_data['title']}")
                    else:
                        print(f"❌ Failed to create conversation: {conv_data['title']}")
            except Exception as e:
                print(f"❌ Error creating conversation {conv_data['title']}: {e}")
                
        return created_conversations

    async def populate_knowledge_graph(self):
        """Add sample entities to the knowledge graph"""
        print("🧠 Populating knowledge graph...")
        
        sample_entities = [
            {
                "name": "Salesforce CRM",
                "entity_type": "system",
                "description": "Customer relationship management system",
                "properties": {
                    "vendor": "Salesforce",
                    "api_version": "v54.0",
                    "authentication": "OAuth 2.0"
                }
            },
            {
                "name": "QuickBooks API",
                "entity_type": "api",
                "description": "Accounting software API for financial data",
                "properties": {
                    "vendor": "Intuit",
                    "rate_limit": "500 requests/minute",
                    "authentication": "OAuth 2.0"
                }
            },
            {
                "name": "Multi-Currency Pattern",
                "entity_type": "pattern",
                "description": "Integration pattern for handling multiple currencies",
                "properties": {
                    "complexity": "high",
                    "components": ["exchange_rate_service", "currency_converter", "tax_calculator"]
                }
            },
            {
                "name": "Webhook Handler Pattern",
                "entity_type": "pattern", 
                "description": "Pattern for processing incoming webhooks reliably",
                "properties": {
                    "reliability": "high",
                    "components": ["signature_verification", "idempotency", "retry_logic"]
                }
            }
        ]
        
        created_entities = []
        for entity in sample_entities:
            try:
                async with self.session.post(f"{API_BASE}/knowledge/entities", json=entity) as response:
                    if response.status == 201:
                        result = await response.json()
                        created_entities.append(result)
                        print(f"✅ Created entity: {entity['name']}")
                    else:
                        print(f"❌ Failed to create entity: {entity['name']}")
            except Exception as e:
                print(f"❌ Error creating entity {entity['name']}: {e}")
                
        return created_entities

    async def test_semantic_search(self):
        """Test the semantic search functionality"""
        print("🔍 Testing semantic search...")
        
        search_queries = [
            "multi-currency integration patterns",
            "webhook error handling",
            "Salesforce API authentication",
            "billing system integration"
        ]
        
        for query in search_queries:
            try:
                async with self.session.post(
                    f"{API_BASE}/knowledge/semantic/search",
                    json={"query": query, "limit": 5}
                ) as response:
                    if response.status == 200:
                        results = await response.json()
                        print(f"✅ Search '{query}': {len(results)} results")
                    else:
                        print(f"❌ Search failed for '{query}'")
            except Exception as e:
                print(f"❌ Search error for '{query}': {e}")

    async def run_complete_demo(self):
        """Run the complete demo sequence"""
        print("🎯 Starting Complete Agentic Integration Platform Demo")
        print("=" * 60)
        
        # Step 1: Create sample data
        integrations = await self.create_sample_integrations()
        conversations = await self.create_sample_conversations()
        entities = await self.populate_knowledge_graph()
        
        # Step 2: Test search functionality
        await self.test_semantic_search()
        
        # Step 3: Display summary
        print("\n" + "=" * 60)
        print("📊 DEMO SUMMARY")
        print("=" * 60)
        print(f"✅ Created {len(integrations)} sample integrations")
        print(f"✅ Created {len(conversations)} MCP conversations")
        print(f"✅ Added {len(entities)} knowledge graph entities")
        print(f"✅ Tested semantic search functionality")
        
        print(f"\n🌐 UI Dashboard: {UI_URL}")
        print("🎮 Demo Features Available:")
        print("  • Dashboard with real integration data")
        print("  • MCP Chat with sample conversations")
        print("  • Knowledge Graph with entities and relationships")
        print("  • Integration Wizard for creating new integrations")
        print("  • Real-time status updates and metrics")
        
        print(f"\n🔗 API Endpoints:")
        print(f"  • Integrations: {API_BASE}/integrations/")
        print(f"  • MCP Chat: {API_BASE}/mcp/conversations")
        print(f"  • Knowledge Graph: {API_BASE}/knowledge/")
        print(f"  • Semantic Search: {API_BASE}/knowledge/semantic/search")

async def main():
    """Main demo function"""
    print("🚀 Agentic Integration Platform - Complete UI Demo")
    print("This demo will populate the system with sample data and showcase all features")
    print("\nMake sure both the backend (port 8000) and frontend (port 3000) are running!")
    
    input("\nPress Enter to continue...")
    
    async with AgenticPlatformDemo() as demo:
        await demo.run_complete_demo()
    
    print("\n🎉 Demo completed! Open http://localhost:3000 to explore the UI")
    print("💡 Try switching between different views and interacting with the components")

if __name__ == "__main__":
    asyncio.run(main())
