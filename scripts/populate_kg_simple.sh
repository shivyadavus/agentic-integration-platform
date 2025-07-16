#!/bin/bash

# Script to populate the knowledge graph with sample entities using the API
# This creates entities for the 4 main types: system, api_endpoint, pattern, integration

API_BASE="http://localhost:8000/api/v1/knowledge"

echo "🚀 Starting knowledge graph population..."

# Function to create entity via API
create_entity() {
    local entity_type="$1"
    local entity_data="$2"
    
    echo "Creating $entity_type entity..."
    curl -s -X POST "$API_BASE/entities" \
        -H "Content-Type: application/json" \
        -d "{
            \"entity_type\": \"$entity_type\",
            \"properties\": $entity_data
        }" | jq -r '.id // "Error"'
}

echo "📊 Creating System entities..."

# Salesforce CRM System
create_entity "system" '{
    "name": "Salesforce CRM",
    "description": "Customer relationship management platform with comprehensive sales, marketing, and service capabilities",
    "vendor": "Salesforce",
    "category": "CRM",
    "api_version": "v58.0",
    "authentication": "OAuth 2.0",
    "rate_limits": "15,000 calls/24hrs",
    "data_formats": ["JSON", "XML", "SOAP"]
}'

# QuickBooks Online System
create_entity "system" '{
    "name": "QuickBooks Online",
    "description": "Cloud-based accounting software for small and medium businesses",
    "vendor": "Intuit",
    "category": "Accounting",
    "api_version": "v3",
    "authentication": "OAuth 2.0",
    "rate_limits": "500 calls/minute",
    "data_formats": ["JSON"]
}'

# Stripe Payment Platform
create_entity "system" '{
    "name": "Stripe Payment Platform",
    "description": "Online payment processing platform for internet businesses",
    "vendor": "Stripe",
    "category": "Payment Processing",
    "api_version": "2023-10-16",
    "authentication": "API Key",
    "rate_limits": "100 calls/second",
    "data_formats": ["JSON"]
}'

# HubSpot Marketing Hub
create_entity "system" '{
    "name": "HubSpot Marketing Hub",
    "description": "Inbound marketing, sales, and service software platform",
    "vendor": "HubSpot",
    "category": "Marketing Automation",
    "api_version": "v3",
    "authentication": "OAuth 2.0",
    "rate_limits": "10,000 calls/day",
    "data_formats": ["JSON"]
}'

echo "🔌 Creating API Endpoint entities..."

# Salesforce REST API
create_entity "api_endpoint" '{
    "name": "Salesforce REST API",
    "description": "RESTful API for accessing Salesforce data and functionality",
    "endpoint": "https://your-instance.salesforce.com/services/data/v58.0/",
    "method": "REST",
    "authentication": "OAuth 2.0",
    "content_type": "application/json",
    "key_endpoints": ["/sobjects/Account", "/sobjects/Contact", "/sobjects/Opportunity"]
}'

# QuickBooks Accounting API
create_entity "api_endpoint" '{
    "name": "QuickBooks Accounting API",
    "description": "API for managing accounting data in QuickBooks Online",
    "endpoint": "https://sandbox-quickbooks.api.intuit.com/v3/company/",
    "method": "REST",
    "authentication": "OAuth 2.0",
    "content_type": "application/json",
    "key_endpoints": ["/customers", "/items", "/invoices", "/payments"]
}'

# Stripe Payments API
create_entity "api_endpoint" '{
    "name": "Stripe Payments API",
    "description": "API for processing payments and managing customer billing",
    "endpoint": "https://api.stripe.com/v1/",
    "method": "REST",
    "authentication": "Bearer Token",
    "content_type": "application/x-www-form-urlencoded",
    "key_endpoints": ["/customers", "/charges", "/subscriptions", "/invoices"]
}'

# HubSpot CRM API
create_entity "api_endpoint" '{
    "name": "HubSpot CRM API",
    "description": "API for managing contacts, companies, and deals in HubSpot",
    "endpoint": "https://api.hubapi.com/crm/v3/",
    "method": "REST",
    "authentication": "OAuth 2.0",
    "content_type": "application/json",
    "key_endpoints": ["/objects/contacts", "/objects/companies", "/objects/deals"]
}'

echo "🔄 Creating Pattern entities..."

# Customer Data Synchronization Pattern
create_entity "pattern" '{
    "name": "Customer Data Synchronization",
    "description": "Pattern for keeping customer data synchronized across multiple systems",
    "pattern_type": "Data Sync",
    "complexity": "Medium",
    "frequency": "Real-time",
    "data_flow": "Bidirectional",
    "common_fields": ["name", "email", "phone", "address"],
    "best_practices": ["Use unique identifiers", "Handle conflicts gracefully", "Implement retry logic"]
}'

# Order-to-Cash Integration Pattern
create_entity "pattern" '{
    "name": "Order-to-Cash Integration",
    "description": "End-to-end pattern for processing orders from creation to payment",
    "pattern_type": "Business Process",
    "complexity": "High",
    "frequency": "Event-driven",
    "data_flow": "Unidirectional",
    "stages": ["Order Creation", "Inventory Check", "Payment Processing", "Fulfillment", "Invoicing"],
    "best_practices": ["Implement saga pattern", "Use event sourcing", "Handle partial failures"]
}'

# Lead Nurturing Workflow Pattern
create_entity "pattern" '{
    "name": "Lead Nurturing Workflow",
    "description": "Pattern for automatically nurturing leads through marketing and sales funnel",
    "pattern_type": "Marketing Automation",
    "complexity": "Medium",
    "frequency": "Scheduled",
    "data_flow": "Unidirectional",
    "triggers": ["Form submission", "Email engagement", "Website behavior"],
    "best_practices": ["Score leads progressively", "Personalize content", "Track engagement metrics"]
}'

# Financial Reporting Aggregation Pattern
create_entity "pattern" '{
    "name": "Financial Reporting Aggregation",
    "description": "Pattern for aggregating financial data from multiple sources for reporting",
    "pattern_type": "Data Aggregation",
    "complexity": "High",
    "frequency": "Batch",
    "data_flow": "Unidirectional",
    "data_sources": ["CRM", "Accounting", "Payment Processing", "E-commerce"],
    "best_practices": ["Ensure data consistency", "Handle currency conversion", "Implement audit trails"]
}'

echo "🔗 Creating Business Object entities..."

# Customer Business Object
create_entity "business_object" '{
    "name": "Customer",
    "description": "Core business entity representing a customer across systems",
    "object_type": "Master Data",
    "common_fields": ["id", "name", "email", "phone", "address", "created_date", "status"],
    "systems": ["Salesforce", "QuickBooks", "Stripe", "HubSpot"],
    "key_identifiers": ["email", "customer_id"],
    "data_quality_rules": ["Email must be valid", "Name is required", "Phone format validation"]
}'

# Invoice Business Object
create_entity "business_object" '{
    "name": "Invoice",
    "description": "Financial document representing a bill for goods or services",
    "object_type": "Transactional Data",
    "common_fields": ["invoice_id", "customer_id", "amount", "due_date", "status", "line_items"],
    "systems": ["QuickBooks", "Stripe", "Salesforce"],
    "key_identifiers": ["invoice_id", "invoice_number"],
    "data_quality_rules": ["Amount must be positive", "Due date must be future", "Customer must exist"]
}'

# Product Business Object
create_entity "business_object" '{
    "name": "Product",
    "description": "Goods or services offered by the business",
    "object_type": "Master Data",
    "common_fields": ["product_id", "name", "description", "price", "category", "status"],
    "systems": ["Salesforce", "QuickBooks", "Stripe"],
    "key_identifiers": ["product_id", "sku"],
    "data_quality_rules": ["Price must be positive", "Name is required", "Category must be valid"]
}'

echo "✨ Knowledge graph population completed!"
echo "🎉 Created entities for all 4 types: system, api_endpoint, pattern, business_object"

# Show summary
echo ""
echo "📈 Summary:"
curl -s "$API_BASE/entities" | jq -r 'group_by(.entity_type) | map({type: .[0].entity_type, count: length}) | .[] | "  \(.type): \(.count) entities"'
