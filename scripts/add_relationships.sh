#!/bin/bash

# Script to add relationships between entities in the knowledge graph

API_BASE="http://localhost:8000/api/v1/knowledge"

echo "🔗 Adding relationships to the knowledge graph..."

# First, let's get the entity IDs
echo "📋 Fetching entity IDs..."

# Get all entities and extract IDs by type
ENTITIES=$(curl -s "$API_BASE/entities")

# Extract IDs for each type (this is a simplified approach)
SALESFORCE_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Salesforce CRM") | .id')
QUICKBOOKS_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "QuickBooks Online") | .id')
STRIPE_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Stripe Payment Platform") | .id')
HUBSPOT_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "HubSpot Marketing Hub") | .id')

SALESFORCE_API_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Salesforce REST API") | .id')
QUICKBOOKS_API_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "QuickBooks Accounting API") | .id')
STRIPE_API_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Stripe Payments API") | .id')
HUBSPOT_API_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "HubSpot CRM API") | .id')

CUSTOMER_SYNC_PATTERN_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Customer Data Synchronization") | .id')
ORDER_CASH_PATTERN_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Order-to-Cash Integration") | .id')
LEAD_NURTURING_PATTERN_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Lead Nurturing Workflow") | .id')
FINANCIAL_REPORTING_PATTERN_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Financial Reporting Aggregation") | .id')

CUSTOMER_OBJECT_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Customer") | .id')
INVOICE_OBJECT_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Invoice") | .id')
PRODUCT_OBJECT_ID=$(echo "$ENTITIES" | jq -r '.[] | select(.properties.name == "Product") | .id')

echo "✅ Entity IDs extracted"

# Function to create relationship
create_relationship() {
    local source_id="$1"
    local target_id="$2"
    local relationship_type="$3"
    local properties="$4"
    
    if [[ -n "$source_id" && -n "$target_id" && "$source_id" != "null" && "$target_id" != "null" ]]; then
        echo "Creating $relationship_type relationship..."
        curl -s -X POST "$API_BASE/relationships" \
            -H "Content-Type: application/json" \
            -d "{
                \"source_id\": \"$source_id\",
                \"target_id\": \"$target_id\",
                \"relationship_type\": \"$relationship_type\",
                \"properties\": $properties
            }" > /dev/null
        echo "  ✅ Created relationship: $relationship_type"
    else
        echo "  ❌ Skipped relationship (missing IDs): $relationship_type"
    fi
}

echo "🔗 Creating system-to-API relationships..."

# Systems to their APIs
create_relationship "$SALESFORCE_ID" "$SALESFORCE_API_ID" "HAS_API" '{
    "description": "Salesforce CRM provides REST API access",
    "api_type": "REST",
    "primary": true
}'

create_relationship "$QUICKBOOKS_ID" "$QUICKBOOKS_API_ID" "HAS_API" '{
    "description": "QuickBooks Online provides accounting API",
    "api_type": "REST",
    "primary": true
}'

create_relationship "$STRIPE_ID" "$STRIPE_API_ID" "HAS_API" '{
    "description": "Stripe provides payments API",
    "api_type": "REST",
    "primary": true
}'

create_relationship "$HUBSPOT_ID" "$HUBSPOT_API_ID" "HAS_API" '{
    "description": "HubSpot provides CRM API access",
    "api_type": "REST",
    "primary": true
}'

echo "📊 Creating pattern-to-system relationships..."

# Customer Sync Pattern relationships
create_relationship "$CUSTOMER_SYNC_PATTERN_ID" "$SALESFORCE_ID" "APPLIES_TO" '{
    "description": "Customer sync pattern commonly used with Salesforce",
    "usage_frequency": "high",
    "complexity": "medium"
}'

create_relationship "$CUSTOMER_SYNC_PATTERN_ID" "$QUICKBOOKS_ID" "APPLIES_TO" '{
    "description": "Customer sync pattern used with QuickBooks",
    "usage_frequency": "high",
    "complexity": "medium"
}'

create_relationship "$CUSTOMER_SYNC_PATTERN_ID" "$HUBSPOT_ID" "APPLIES_TO" '{
    "description": "Customer sync pattern used with HubSpot",
    "usage_frequency": "medium",
    "complexity": "low"
}'

# Order-to-Cash Pattern relationships
create_relationship "$ORDER_CASH_PATTERN_ID" "$SALESFORCE_ID" "APPLIES_TO" '{
    "description": "Order-to-cash process starts in Salesforce",
    "usage_frequency": "high",
    "complexity": "high"
}'

create_relationship "$ORDER_CASH_PATTERN_ID" "$STRIPE_ID" "APPLIES_TO" '{
    "description": "Stripe handles payment processing in order-to-cash",
    "usage_frequency": "high",
    "complexity": "medium"
}'

create_relationship "$ORDER_CASH_PATTERN_ID" "$QUICKBOOKS_ID" "APPLIES_TO" '{
    "description": "QuickBooks handles invoicing in order-to-cash",
    "usage_frequency": "high",
    "complexity": "medium"
}'

# Lead Nurturing Pattern relationships
create_relationship "$LEAD_NURTURING_PATTERN_ID" "$HUBSPOT_ID" "APPLIES_TO" '{
    "description": "HubSpot specializes in lead nurturing workflows",
    "usage_frequency": "very_high",
    "complexity": "medium"
}'

create_relationship "$LEAD_NURTURING_PATTERN_ID" "$SALESFORCE_ID" "APPLIES_TO" '{
    "description": "Salesforce can implement lead nurturing",
    "usage_frequency": "medium",
    "complexity": "high"
}'

# Financial Reporting Pattern relationships
create_relationship "$FINANCIAL_REPORTING_PATTERN_ID" "$QUICKBOOKS_ID" "APPLIES_TO" '{
    "description": "QuickBooks is primary source for financial reporting",
    "usage_frequency": "very_high",
    "complexity": "low"
}'

create_relationship "$FINANCIAL_REPORTING_PATTERN_ID" "$STRIPE_ID" "APPLIES_TO" '{
    "description": "Stripe provides payment data for financial reports",
    "usage_frequency": "high",
    "complexity": "medium"
}'

create_relationship "$FINANCIAL_REPORTING_PATTERN_ID" "$SALESFORCE_ID" "APPLIES_TO" '{
    "description": "Salesforce provides sales data for financial reports",
    "usage_frequency": "medium",
    "complexity": "medium"
}'

echo "🏢 Creating business object relationships..."

# Customer object relationships
create_relationship "$CUSTOMER_OBJECT_ID" "$SALESFORCE_ID" "STORED_IN" '{
    "description": "Customer data is managed in Salesforce CRM",
    "data_quality": "high",
    "is_master": true
}'

create_relationship "$CUSTOMER_OBJECT_ID" "$QUICKBOOKS_ID" "STORED_IN" '{
    "description": "Customer billing info stored in QuickBooks",
    "data_quality": "high",
    "is_master": false
}'

create_relationship "$CUSTOMER_OBJECT_ID" "$STRIPE_ID" "STORED_IN" '{
    "description": "Customer payment info stored in Stripe",
    "data_quality": "high",
    "is_master": false
}'

create_relationship "$CUSTOMER_OBJECT_ID" "$HUBSPOT_ID" "STORED_IN" '{
    "description": "Customer marketing data stored in HubSpot",
    "data_quality": "medium",
    "is_master": false
}'

# Invoice object relationships
create_relationship "$INVOICE_OBJECT_ID" "$QUICKBOOKS_ID" "STORED_IN" '{
    "description": "Invoices are primarily managed in QuickBooks",
    "data_quality": "very_high",
    "is_master": true
}'

create_relationship "$INVOICE_OBJECT_ID" "$STRIPE_ID" "STORED_IN" '{
    "description": "Payment invoices stored in Stripe",
    "data_quality": "high",
    "is_master": false
}'

create_relationship "$INVOICE_OBJECT_ID" "$SALESFORCE_ID" "STORED_IN" '{
    "description": "Sales invoices tracked in Salesforce",
    "data_quality": "medium",
    "is_master": false
}'

# Product object relationships
create_relationship "$PRODUCT_OBJECT_ID" "$SALESFORCE_ID" "STORED_IN" '{
    "description": "Product catalog managed in Salesforce",
    "data_quality": "high",
    "is_master": true
}'

create_relationship "$PRODUCT_OBJECT_ID" "$QUICKBOOKS_ID" "STORED_IN" '{
    "description": "Product pricing stored in QuickBooks",
    "data_quality": "high",
    "is_master": false
}'

create_relationship "$PRODUCT_OBJECT_ID" "$STRIPE_ID" "STORED_IN" '{
    "description": "Product pricing for payments in Stripe",
    "data_quality": "medium",
    "is_master": false
}'

echo "🔄 Creating cross-pattern relationships..."

# Pattern interdependencies
create_relationship "$CUSTOMER_SYNC_PATTERN_ID" "$ORDER_CASH_PATTERN_ID" "ENABLES" '{
    "description": "Customer sync enables order-to-cash process",
    "dependency_type": "prerequisite",
    "strength": "high"
}'

create_relationship "$LEAD_NURTURING_PATTERN_ID" "$CUSTOMER_SYNC_PATTERN_ID" "FEEDS_INTO" '{
    "description": "Lead nurturing creates customers that need syncing",
    "dependency_type": "sequential",
    "strength": "medium"
}'

create_relationship "$ORDER_CASH_PATTERN_ID" "$FINANCIAL_REPORTING_PATTERN_ID" "FEEDS_INTO" '{
    "description": "Order-to-cash generates data for financial reporting",
    "dependency_type": "data_flow",
    "strength": "very_high"
}'

echo "✨ Relationship creation completed!"

# Show summary
echo ""
echo "📈 Relationship Summary:"
curl -s "$API_BASE/relationships" | jq -r 'group_by(.relationship_type) | map({type: .[0].relationship_type, count: length}) | .[] | "  \(.type): \(.count) relationships"'

echo ""
echo "🎉 Knowledge graph is now fully populated with entities and relationships!"
