#!/usr/bin/env python3
"""
Script to populate the knowledge graph with sample entities and relationships
for the 4 main types: System, API, Pattern, Integration
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from uuid import uuid4

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.knowledge.graph_service import KnowledgeGraphService
from app.models.knowledge import Entity, Relationship


async def populate_knowledge_graph():
    """Populate the knowledge graph with sample data."""
    
    # Initialize the knowledge graph service
    kg_service = KnowledgeGraphService()
    
    print("🚀 Starting knowledge graph population...")
    
    # Sample Systems
    systems = [
        {
            "name": "Salesforce CRM",
            "entity_type": "system",
            "description": "Customer relationship management platform with comprehensive sales, marketing, and service capabilities",
            "properties": {
                "vendor": "Salesforce",
                "category": "CRM",
                "api_version": "v58.0",
                "authentication": "OAuth 2.0",
                "rate_limits": "15,000 calls/24hrs",
                "data_formats": ["JSON", "XML", "SOAP"]
            }
        },
        {
            "name": "QuickBooks Online",
            "entity_type": "system", 
            "description": "Cloud-based accounting software for small and medium businesses",
            "properties": {
                "vendor": "Intuit",
                "category": "Accounting",
                "api_version": "v3",
                "authentication": "OAuth 2.0",
                "rate_limits": "500 calls/minute",
                "data_formats": ["JSON"]
            }
        },
        {
            "name": "Stripe Payment Platform",
            "entity_type": "system",
            "description": "Online payment processing platform for internet businesses",
            "properties": {
                "vendor": "Stripe",
                "category": "Payment Processing",
                "api_version": "2023-10-16",
                "authentication": "API Key",
                "rate_limits": "100 calls/second",
                "data_formats": ["JSON"]
            }
        },
        {
            "name": "HubSpot Marketing Hub",
            "entity_type": "system",
            "description": "Inbound marketing, sales, and service software platform",
            "properties": {
                "vendor": "HubSpot",
                "category": "Marketing Automation",
                "api_version": "v3",
                "authentication": "OAuth 2.0",
                "rate_limits": "10,000 calls/day",
                "data_formats": ["JSON"]
            }
        }
    ]
    
    # Sample APIs
    apis = [
        {
            "name": "Salesforce REST API",
            "entity_type": "api",
            "description": "RESTful API for accessing Salesforce data and functionality",
            "properties": {
                "endpoint": "https://your-instance.salesforce.com/services/data/v58.0/",
                "method": "REST",
                "authentication": "OAuth 2.0",
                "content_type": "application/json",
                "key_endpoints": ["/sobjects/Account", "/sobjects/Contact", "/sobjects/Opportunity"]
            }
        },
        {
            "name": "QuickBooks Accounting API",
            "entity_type": "api",
            "description": "API for managing accounting data in QuickBooks Online",
            "properties": {
                "endpoint": "https://sandbox-quickbooks.api.intuit.com/v3/company/",
                "method": "REST",
                "authentication": "OAuth 2.0",
                "content_type": "application/json",
                "key_endpoints": ["/customers", "/items", "/invoices", "/payments"]
            }
        },
        {
            "name": "Stripe Payments API",
            "entity_type": "api",
            "description": "API for processing payments and managing customer billing",
            "properties": {
                "endpoint": "https://api.stripe.com/v1/",
                "method": "REST",
                "authentication": "Bearer Token",
                "content_type": "application/x-www-form-urlencoded",
                "key_endpoints": ["/customers", "/charges", "/subscriptions", "/invoices"]
            }
        },
        {
            "name": "HubSpot CRM API",
            "entity_type": "api",
            "description": "API for managing contacts, companies, and deals in HubSpot",
            "properties": {
                "endpoint": "https://api.hubapi.com/crm/v3/",
                "method": "REST",
                "authentication": "OAuth 2.0",
                "content_type": "application/json",
                "key_endpoints": ["/objects/contacts", "/objects/companies", "/objects/deals"]
            }
        }
    ]
    
    # Sample Patterns
    patterns = [
        {
            "name": "Customer Data Synchronization",
            "entity_type": "pattern",
            "description": "Pattern for keeping customer data synchronized across multiple systems",
            "properties": {
                "pattern_type": "Data Sync",
                "complexity": "Medium",
                "frequency": "Real-time",
                "data_flow": "Bidirectional",
                "common_fields": ["name", "email", "phone", "address"],
                "best_practices": ["Use unique identifiers", "Handle conflicts gracefully", "Implement retry logic"]
            }
        },
        {
            "name": "Order-to-Cash Integration",
            "entity_type": "pattern",
            "description": "End-to-end pattern for processing orders from creation to payment",
            "properties": {
                "pattern_type": "Business Process",
                "complexity": "High",
                "frequency": "Event-driven",
                "data_flow": "Unidirectional",
                "stages": ["Order Creation", "Inventory Check", "Payment Processing", "Fulfillment", "Invoicing"],
                "best_practices": ["Implement saga pattern", "Use event sourcing", "Handle partial failures"]
            }
        },
        {
            "name": "Lead Nurturing Workflow",
            "entity_type": "pattern",
            "description": "Pattern for automatically nurturing leads through marketing and sales funnel",
            "properties": {
                "pattern_type": "Marketing Automation",
                "complexity": "Medium",
                "frequency": "Scheduled",
                "data_flow": "Unidirectional",
                "triggers": ["Form submission", "Email engagement", "Website behavior"],
                "best_practices": ["Score leads progressively", "Personalize content", "Track engagement metrics"]
            }
        },
        {
            "name": "Financial Reporting Aggregation",
            "entity_type": "pattern",
            "description": "Pattern for aggregating financial data from multiple sources for reporting",
            "properties": {
                "pattern_type": "Data Aggregation",
                "complexity": "High",
                "frequency": "Batch",
                "data_flow": "Unidirectional",
                "data_sources": ["CRM", "Accounting", "Payment Processing", "E-commerce"],
                "best_practices": ["Ensure data consistency", "Handle currency conversion", "Implement audit trails"]
            }
        }
    ]
    
    # Sample Integrations
    integrations = [
        {
            "name": "Salesforce-QuickBooks Customer Sync",
            "entity_type": "integration",
            "description": "Real-time synchronization of customer data between Salesforce CRM and QuickBooks",
            "properties": {
                "status": "Active",
                "integration_type": "Bidirectional Sync",
                "frequency": "Real-time",
                "last_sync": "2024-07-16T10:30:00Z",
                "records_synced": 1250,
                "error_rate": "0.2%",
                "data_mapping": {
                    "Account.Name": "Customer.Name",
                    "Account.Email": "Customer.Email",
                    "Account.Phone": "Customer.Phone"
                }
            }
        },
        {
            "name": "Stripe-QuickBooks Payment Integration",
            "entity_type": "integration",
            "description": "Automatic creation of invoices and payment records in QuickBooks from Stripe transactions",
            "properties": {
                "status": "Active",
                "integration_type": "Unidirectional",
                "frequency": "Event-driven",
                "last_sync": "2024-07-16T11:15:00Z",
                "records_synced": 890,
                "error_rate": "0.1%",
                "webhook_url": "https://api.example.com/webhooks/stripe"
            }
        },
        {
            "name": "HubSpot-Salesforce Lead Transfer",
            "entity_type": "integration",
            "description": "Transfer qualified leads from HubSpot marketing to Salesforce sales team",
            "properties": {
                "status": "Active",
                "integration_type": "Unidirectional",
                "frequency": "Real-time",
                "last_sync": "2024-07-16T09:45:00Z",
                "records_synced": 340,
                "error_rate": "0.3%",
                "qualification_criteria": ["Lead Score > 80", "Email Engagement > 50%"]
            }
        }
    ]
    
    # Create entities
    created_entities = {}
    
    print("📊 Creating System entities...")
    for system_data in systems:
        entity = Entity(
            id=str(uuid4()),
            name=system_data["name"],
            entity_type=system_data["entity_type"],
            semantic_label=system_data["name"],
            canonical_name=system_data["name"],
            aliases=[],
            schema_definition={},
            data_type="system",
            constraints={},
            system_id=None,
            api_path=None,
            embedding_vector=[],
            embedding_model="text-embedding-ada-002",
            usage_count=0,
            confidence_score=0.95,
            quality_score=0.90,
            verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Set properties
        for key, value in system_data["properties"].items():
            setattr(entity, key, value)
        
        entity_id = await kg_service.create_entity(entity)
        created_entities[system_data["name"]] = entity_id
        print(f"  ✅ Created system: {system_data['name']}")
    
    print("🔌 Creating API entities...")
    for api_data in apis:
        entity = Entity(
            id=str(uuid4()),
            name=api_data["name"],
            entity_type=api_data["entity_type"],
            semantic_label=api_data["name"],
            canonical_name=api_data["name"],
            aliases=[],
            schema_definition={},
            data_type="api",
            constraints={},
            system_id=None,
            api_path=api_data["properties"].get("endpoint", ""),
            embedding_vector=[],
            embedding_model="text-embedding-ada-002",
            usage_count=0,
            confidence_score=0.90,
            quality_score=0.85,
            verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Set properties
        for key, value in api_data["properties"].items():
            setattr(entity, key, value)
        
        entity_id = await kg_service.create_entity(entity)
        created_entities[api_data["name"]] = entity_id
        print(f"  ✅ Created API: {api_data['name']}")
    
    print("🔄 Creating Pattern entities...")
    for pattern_data in patterns:
        entity = Entity(
            id=str(uuid4()),
            name=pattern_data["name"],
            entity_type=pattern_data["entity_type"],
            semantic_label=pattern_data["name"],
            canonical_name=pattern_data["name"],
            aliases=[],
            schema_definition={},
            data_type="pattern",
            constraints={},
            system_id=None,
            api_path=None,
            embedding_vector=[],
            embedding_model="text-embedding-ada-002",
            usage_count=0,
            confidence_score=0.85,
            quality_score=0.80,
            verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Set properties
        for key, value in pattern_data["properties"].items():
            setattr(entity, key, value)
        
        entity_id = await kg_service.create_entity(entity)
        created_entities[pattern_data["name"]] = entity_id
        print(f"  ✅ Created pattern: {pattern_data['name']}")
    
    print("🔗 Creating Integration entities...")
    for integration_data in integrations:
        entity = Entity(
            id=str(uuid4()),
            name=integration_data["name"],
            entity_type=integration_data["entity_type"],
            semantic_label=integration_data["name"],
            canonical_name=integration_data["name"],
            aliases=[],
            schema_definition={},
            data_type="integration",
            constraints={},
            system_id=None,
            api_path=None,
            embedding_vector=[],
            embedding_model="text-embedding-ada-002",
            usage_count=0,
            confidence_score=0.80,
            quality_score=0.75,
            verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Set properties
        for key, value in integration_data["properties"].items():
            setattr(entity, key, value)
        
        entity_id = await kg_service.create_entity(entity)
        created_entities[integration_data["name"]] = entity_id
        print(f"  ✅ Created integration: {integration_data['name']}")
    
    print(f"🎉 Successfully created {len(created_entities)} entities!")
    print("✨ Knowledge graph population completed!")


if __name__ == "__main__":
    asyncio.run(populate_knowledge_graph())
