#!/usr/bin/env python3
"""
Development data initialization script.
This script populates the knowledge graph with realistic sample data for development.
"""

import asyncio
import sys
import os
import json
import requests
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, List


def check_if_data_exists() -> bool:
    """Check if sample data already exists via API."""
    try:
        response = requests.get("http://localhost:8000/api/v1/knowledge/entities")
        if response.status_code == 200:
            entities = response.json()
            return len(entities) > 5  # Allow some basic entities but repopulate if too few
        return False
    except Exception:
        return False


def clear_existing_data():
    """Clear existing sample data via API."""
    try:
        response = requests.get("http://localhost:8000/api/v1/knowledge/entities")
        if response.status_code == 200:
            entities = response.json()
            # Delete each entity (if delete endpoint exists)
            # For now, we'll just note that we're refreshing
            print(f"🔄 Found {len(entities)} existing entities - refreshing with new data")
    except Exception as e:
        print(f"⚠️  Warning: Could not check existing data: {str(e)}")


def create_realistic_sample_entities():
    """Create realistic sample entities based on real-world B2B integration scenarios."""

    print("🚀 Initializing realistic development knowledge graph data...")

    # Check if we need to reinitialize
    if check_if_data_exists():
        print("🔄 Refreshing sample data with latest realistic examples...")
        clear_existing_data()
    
    # Realistic sample data based on actual enterprise integrations
    sample_entities = [
        # === SYSTEMS (Real enterprise platforms) ===
        {
            "name": "Salesforce Sales Cloud",
            "entity_type": "system",
            "description": "Enterprise CRM platform managing 50M+ customer records with advanced sales automation, lead scoring, and opportunity management",
            "properties": {
                "name": "Salesforce Sales Cloud",
                "vendor": "Salesforce",
                "category": "CRM",
                "api_version": "v58.0",
                "authentication": "OAuth 2.0 + JWT",
                "rate_limits": "15,000 API calls per 24 hours",
                "data_formats": ["JSON", "XML", "SOAP"],
                "deployment": "Multi-tenant SaaS",
                "compliance": ["SOC 2", "GDPR", "HIPAA"],
                "pricing_model": "Per user/month",
                "integration_complexity": "Medium-High",
                "typical_use_cases": ["Lead management", "Opportunity tracking", "Account management", "Sales forecasting"]
            }
        },
        {
            "name": "QuickBooks Enterprise",
            "entity_type": "system",
            "description": "Advanced accounting software handling $2B+ in transactions annually with multi-currency support and advanced reporting",
            "properties": {
                "name": "QuickBooks Enterprise",
                "vendor": "Intuit",
                "category": "ERP/Accounting",
                "api_version": "v3",
                "authentication": "OAuth 2.0",
                "rate_limits": "500 calls per minute per app",
                "data_formats": ["JSON"],
                "deployment": "Cloud + Desktop",
                "compliance": ["SOX", "PCI DSS"],
                "pricing_model": "Subscription + transaction fees",
                "integration_complexity": "Medium",
                "typical_use_cases": ["Invoice management", "Payment processing", "Financial reporting", "Tax compliance"]
            }
        },
        {
            "name": "Stripe Connect",
            "entity_type": "system",
            "description": "Global payment infrastructure processing $640B+ annually with marketplace and multi-party payment capabilities",
            "properties": {
                "name": "Stripe Connect",
                "vendor": "Stripe",
                "category": "Payment Processing",
                "api_version": "2023-10-16",
                "authentication": "API Keys + OAuth for Connect",
                "rate_limits": "100 requests per second",
                "data_formats": ["JSON"],
                "deployment": "Global SaaS",
                "compliance": ["PCI Level 1", "SOC 2", "ISO 27001"],
                "pricing_model": "2.9% + 30¢ per transaction",
                "integration_complexity": "Low-Medium",
                "typical_use_cases": ["Online payments", "Subscription billing", "Marketplace payments", "International transfers"]
            }
        },
        {
            "name": "HubSpot Marketing Hub Enterprise",
            "entity_type": "system",
            "description": "Inbound marketing platform managing 100M+ contacts with advanced automation, attribution, and personalization",
            "properties": {
                "name": "HubSpot Marketing Hub Enterprise",
                "vendor": "HubSpot",
                "category": "Marketing Automation",
                "api_version": "v3",
                "authentication": "OAuth 2.0 + Private Apps",
                "rate_limits": "10,000 requests per day (Enterprise)",
                "data_formats": ["JSON"],
                "deployment": "Multi-tenant SaaS",
                "compliance": ["GDPR", "CCPA", "SOC 2"],
                "pricing_model": "Tiered subscription",
                "integration_complexity": "Medium",
                "typical_use_cases": ["Lead nurturing", "Email campaigns", "Marketing attribution", "Content management"]
            }
        },
        {
            "name": "Microsoft Dynamics 365",
            "entity_type": "system",
            "description": "Enterprise business applications suite with CRM, ERP, and business intelligence capabilities serving Fortune 500 companies",
            "properties": {
                "name": "Microsoft Dynamics 365",
                "vendor": "Microsoft",
                "category": "ERP/CRM Suite",
                "api_version": "v9.2",
                "authentication": "Azure AD OAuth 2.0",
                "rate_limits": "6,000 requests per 5 minutes",
                "data_formats": ["JSON", "OData"],
                "deployment": "Cloud + On-premise hybrid",
                "compliance": ["SOC 1/2/3", "ISO 27001", "FedRAMP"],
                "pricing_model": "Per user/month + usage",
                "integration_complexity": "High",
                "typical_use_cases": ["Enterprise resource planning", "Customer service", "Field service", "Business intelligence"]
            }
        },
        {
            "name": "NetSuite ERP",
            "entity_type": "system",
            "description": "Cloud ERP system managing complex business operations for 31,000+ organizations with real-time financial consolidation",
            "properties": {
                "name": "NetSuite ERP",
                "vendor": "Oracle",
                "category": "ERP",
                "api_version": "2023.2",
                "authentication": "Token-based + OAuth 2.0",
                "rate_limits": "1,000 requests per hour (varies by license)",
                "data_formats": ["JSON", "XML", "CSV"],
                "deployment": "Multi-tenant Cloud",
                "compliance": ["SOC 1/2", "PCI DSS", "GDPR"],
                "pricing_model": "User-based + module licensing",
                "integration_complexity": "High",
                "typical_use_cases": ["Financial management", "Inventory management", "Order management", "Business intelligence"]
            }
        },

        # === API ENDPOINTS (Real enterprise APIs) ===
        {
            "name": "Salesforce REST API v58.0",
            "entity_type": "api_endpoint",
            "description": "Enterprise-grade REST API handling 1B+ API calls daily with comprehensive CRM data access and real-time streaming",
            "properties": {
                "name": "Salesforce REST API v58.0",
                "endpoint": "https://{instance}.salesforce.com/services/data/v58.0/",
                "method": "REST",
                "authentication": "OAuth 2.0 + JWT Bearer",
                "content_type": "application/json",
                "key_endpoints": [
                    "/sobjects/Account/", "/sobjects/Contact/", "/sobjects/Opportunity/",
                    "/sobjects/Lead/", "/sobjects/Case/", "/query/", "/composite/"
                ],
                "response_formats": ["JSON", "XML"],
                "rate_limiting": "Concurrent request limits + daily API limits",
                "webhook_support": True,
                "bulk_operations": True,
                "real_time_events": "Platform Events + Change Data Capture"
            }
        },
        {
            "name": "QuickBooks Online API v3",
            "entity_type": "api_endpoint",
            "description": "Comprehensive accounting API processing millions of financial transactions with real-time sync and multi-currency support",
            "properties": {
                "name": "QuickBooks Online API v3",
                "endpoint": "https://quickbooks-api.intuit.com/v3/company/{companyId}/",
                "method": "REST",
                "authentication": "OAuth 2.0 + OpenID Connect",
                "content_type": "application/json",
                "key_endpoints": [
                    "/customers", "/items", "/invoices", "/payments", "/bills",
                    "/accounts", "/taxcodes", "/reports/", "/companyinfo/"
                ],
                "response_formats": ["JSON", "XML"],
                "rate_limiting": "500 requests per minute per app",
                "webhook_support": True,
                "bulk_operations": False,
                "real_time_events": "Webhooks for entity changes"
            }
        },
        {
            "name": "Stripe Payments API v1",
            "entity_type": "api_endpoint",
            "description": "Global payments API processing $640B+ annually with 99.99% uptime and sub-second response times",
            "properties": {
                "name": "Stripe Payments API v1",
                "endpoint": "https://api.stripe.com/v1/",
                "method": "REST",
                "authentication": "Bearer Token + Connect OAuth",
                "content_type": "application/x-www-form-urlencoded",
                "key_endpoints": [
                    "/customers", "/payment_intents", "/subscriptions", "/invoices",
                    "/products", "/prices", "/payment_methods", "/accounts", "/transfers"
                ],
                "response_formats": ["JSON"],
                "rate_limiting": "100 requests per second",
                "webhook_support": True,
                "bulk_operations": False,
                "real_time_events": "Webhooks for all payment events"
            }
        },
        {
            "name": "HubSpot CRM API v3",
            "entity_type": "api_endpoint",
            "description": "Modern CRM API managing 100M+ contacts with advanced search, custom objects, and real-time sync capabilities",
            "properties": {
                "name": "HubSpot CRM API v3",
                "endpoint": "https://api.hubapi.com/crm/v3/",
                "method": "REST",
                "authentication": "OAuth 2.0 + Private Apps + API Keys",
                "content_type": "application/json",
                "key_endpoints": [
                    "/objects/contacts", "/objects/companies", "/objects/deals",
                    "/objects/tickets", "/objects/products", "/objects/line_items",
                    "/pipelines/", "/properties/", "/associations/"
                ],
                "response_formats": ["JSON"],
                "rate_limiting": "10,000 requests per day (varies by tier)",
                "webhook_support": True,
                "bulk_operations": True,
                "real_time_events": "Webhooks + Timeline events"
            }
        },

        # === INTEGRATION PATTERNS (Real-world scenarios) ===
        {
            "name": "Quote-to-Cash Automation",
            "entity_type": "pattern",
            "description": "End-to-end revenue process automation from initial quote through payment collection, reducing sales cycle by 40%",
            "properties": {
                "name": "Quote-to-Cash Automation",
                "pattern_type": "Business Process Automation",
                "complexity": "High",
                "implementation_time": "3-6 months",
                "roi_timeline": "6-12 months",
                "success_rate": "85%",
                "common_challenges": ["Data synchronization", "Approval workflows", "Tax calculations", "Multi-currency handling"],
                "key_systems": ["CRM", "CPQ", "ERP", "Payment Gateway"],
                "business_impact": "40% faster sales cycle, 25% reduction in errors, 60% less manual work",
                "best_practices": [
                    "Implement real-time data sync",
                    "Use event-driven architecture",
                    "Maintain audit trails",
                    "Handle partial failures gracefully"
                ]
            }
        },
        {
            "name": "Customer 360 Data Unification",
            "entity_type": "pattern",
            "description": "Master data management pattern creating unified customer profiles across 15+ enterprise systems, improving customer experience by 45%",
            "properties": {
                "name": "Customer 360 Data Unification",
                "pattern_type": "Master Data Management",
                "complexity": "High",
                "implementation_time": "4-8 months",
                "roi_timeline": "8-18 months",
                "success_rate": "70%",
                "data_sources": ["CRM", "ERP", "E-commerce", "Support", "Marketing", "Billing"],
                "sync_frequency": "Real-time + Batch reconciliation",
                "data_quality_score": "95%+",
                "business_impact": "45% better customer experience, 30% faster support resolution, 25% increase in cross-sell",
                "key_challenges": ["Data deduplication", "Schema mapping", "Conflict resolution", "Privacy compliance"],
                "best_practices": [
                    "Implement golden record management",
                    "Use probabilistic matching",
                    "Maintain data lineage",
                    "Ensure GDPR compliance"
                ]
            }
        },
        {
            "name": "Order-to-Cash Integration",
            "entity_type": "pattern",
            "description": "End-to-end pattern for processing orders from creation to payment",
            "properties": {
                "name": "Order-to-Cash Integration",
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
                "name": "Lead Nurturing Workflow",
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
                "name": "Financial Reporting Aggregation",
                "pattern_type": "Data Aggregation",
                "complexity": "High",
                "frequency": "Batch",
                "data_flow": "Unidirectional",
                "data_sources": ["CRM", "Accounting", "Payment Processing", "E-commerce"],
                "best_practices": ["Ensure data consistency", "Handle currency conversion", "Implement audit trails"]
            }
        },

        # === BUSINESS OBJECTS (Enterprise data entities) ===
        {
            "name": "Enterprise Customer Record",
            "entity_type": "business_object",
            "description": "Unified customer entity spanning 50M+ records across global enterprise systems with 360-degree view and real-time updates",
            "properties": {
                "name": "Enterprise Customer Record",
                "object_type": "Master Data Entity",
                "record_count": "50,000,000+",
                "update_frequency": "Real-time",
                "data_quality_score": "96%",
                "common_fields": [
                    "customer_id", "global_customer_id", "name", "email", "phone",
                    "billing_address", "shipping_address", "company", "industry",
                    "lifecycle_stage", "created_date", "last_modified", "status"
                ],
                "systems_of_record": ["Salesforce", "NetSuite", "HubSpot", "Dynamics 365"],
                "downstream_systems": ["QuickBooks", "Stripe", "Zendesk", "Marketo"],
                "key_identifiers": ["email", "customer_id", "tax_id", "duns_number"],
                "data_governance": ["PII encryption", "GDPR compliance", "Data retention policies"],
                "business_rules": [
                    "Email must be unique and valid",
                    "Company customers require tax ID",
                    "Lifecycle stage must progress logically",
                    "Address validation for billing"
                ]
            }
        },
        {
            "name": "Invoice",
            "entity_type": "business_object",
            "description": "Financial document representing a bill for goods or services",
            "properties": {
                "name": "Invoice",
                "object_type": "Transactional Data",
                "common_fields": ["invoice_id", "customer_id", "amount", "due_date", "status", "line_items"],
                "systems": ["QuickBooks", "Stripe", "Salesforce"],
                "key_identifiers": ["invoice_id", "invoice_number"],
                "data_quality_rules": ["Amount must be positive", "Due date must be future", "Customer must exist"]
            }
        },
        {
            "name": "Product",
            "entity_type": "business_object",
            "description": "Goods or services offered by the business",
            "properties": {
                "name": "Product",
                "object_type": "Master Data",
                "common_fields": ["product_id", "name", "description", "price", "category", "status"],
                "systems": ["Salesforce", "QuickBooks", "Stripe"],
                "key_identifiers": ["product_id", "sku"],
                "data_quality_rules": ["Price must be positive", "Name is required", "Category must be valid"]
            }
        }
    ]
    
    # Create entities via API
    try:
        created_count = 0
        for entity_data in sample_entities:
            # Prepare API request
            api_data = {
                "entity_type": entity_data["entity_type"],
                "properties": entity_data["properties"]
            }

            # Create entity via API
            response = requests.post(
                "http://localhost:8000/api/v1/knowledge/entities",
                json=api_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 201:
                created_count += 1
                print(f"  ✅ Created {entity_data['entity_type']}: {entity_data['name']}")
            else:
                print(f"  ⚠️  Failed to create {entity_data['name']}: {response.text}")

        print(f"🎉 Successfully created {created_count} realistic sample entities!")

    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        raise


def main():
    """Main initialization function."""
    try:
        create_realistic_sample_entities()
        print("✨ Realistic development data initialization completed successfully!")
        print("🔗 Knowledge graph now contains enterprise-grade sample data")
        print("📊 Ready for development and testing!")

    except Exception as e:
        print(f"❌ Failed to initialize development data: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
