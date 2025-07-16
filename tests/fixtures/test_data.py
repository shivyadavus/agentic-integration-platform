"""
Test data constants and utilities for the agentic integration platform.

This module provides static test data, sample configurations, and utility
functions for creating consistent test scenarios.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


# Sample AI responses for mocking
SAMPLE_AI_RESPONSES = {
    "anthropic": {
        "code_generation": {
            "content": [
                {
                    "type": "text",
                    "text": "Here's the generated integration code:\n\n```python\ndef sync_data():\n    # Implementation here\n    pass\n```"
                }
            ],
            "model": "claude-3-sonnet-20240229",
            "role": "assistant",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50
            }
        },
        "analysis": {
            "content": [
                {
                    "type": "text", 
                    "text": "Based on the integration requirements, I recommend using a webhook-based approach for real-time synchronization."
                }
            ],
            "model": "claude-3-sonnet-20240229",
            "role": "assistant",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 150,
                "output_tokens": 75
            }
        }
    },
    "openai": {
        "code_generation": {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Here's the generated integration code:\n\n```python\ndef sync_data():\n    # Implementation here\n    pass\n```"
                    },
                    "finish_reason": "stop"
                }
            ],
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        },
        "analysis": {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Based on the integration requirements, I recommend using a webhook-based approach for real-time synchronization."
                    },
                    "finish_reason": "stop"
                }
            ],
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 75,
                "total_tokens": 225
            }
        }
    }
}


# Sample system configurations
SAMPLE_SYSTEM_CONFIGS = {
    "salesforce": {
        "name": "Salesforce CRM",
        "type": "crm",
        "base_url": "https://api.salesforce.com",
        "authentication": {
            "type": "oauth2",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "scope": "api"
        },
        "endpoints": {
            "accounts": "/services/data/v58.0/sobjects/Account",
            "contacts": "/services/data/v58.0/sobjects/Contact",
            "opportunities": "/services/data/v58.0/sobjects/Opportunity"
        },
        "rate_limits": {
            "requests_per_hour": 1000,
            "burst_limit": 100
        }
    },
    "hubspot": {
        "name": "HubSpot CRM",
        "type": "crm",
        "base_url": "https://api.hubapi.com",
        "authentication": {
            "type": "api_key",
            "header": "Authorization",
            "prefix": "Bearer"
        },
        "endpoints": {
            "contacts": "/crm/v3/objects/contacts",
            "companies": "/crm/v3/objects/companies",
            "deals": "/crm/v3/objects/deals"
        },
        "rate_limits": {
            "requests_per_second": 10,
            "daily_limit": 40000
        }
    },
    "slack": {
        "name": "Slack",
        "type": "communication",
        "base_url": "https://slack.com/api",
        "authentication": {
            "type": "bearer_token",
            "header": "Authorization"
        },
        "endpoints": {
            "channels": "/conversations.list",
            "messages": "/chat.postMessage",
            "users": "/users.list"
        },
        "rate_limits": {
            "tier": "tier_2",
            "requests_per_minute": 20
        }
    }
}


# Sample integration patterns
SAMPLE_INTEGRATION_PATTERNS = {
    "crm_sync": {
        "name": "CRM Contact Synchronization",
        "description": "Synchronize contacts between CRM systems",
        "pattern_type": "sync",
        "template": {
            "trigger": {
                "type": "webhook",
                "events": ["contact.created", "contact.updated"]
            },
            "transformation": {
                "field_mappings": {
                    "email": "email",
                    "firstName": "first_name",
                    "lastName": "last_name",
                    "company": "company_name"
                },
                "data_validation": {
                    "required_fields": ["email"],
                    "email_format": True
                }
            },
            "destination": {
                "system": "target_crm",
                "endpoint": "contacts",
                "method": "POST"
            },
            "error_handling": {
                "retry_count": 3,
                "retry_delay": 5,
                "dead_letter_queue": True
            }
        },
        "confidence_score": 0.95,
        "usage_count": 150
    },
    "notification_workflow": {
        "name": "Deal Notification Workflow",
        "description": "Send notifications when deals reach certain stages",
        "pattern_type": "workflow",
        "template": {
            "trigger": {
                "type": "field_change",
                "field": "deal_stage",
                "conditions": {
                    "new_value": ["closed_won", "closed_lost"]
                }
            },
            "actions": [
                {
                    "type": "notification",
                    "channel": "slack",
                    "template": "Deal {{deal.name}} has been {{deal.stage}}"
                },
                {
                    "type": "email",
                    "recipients": ["sales@company.com"],
                    "template": "deal_notification"
                }
            ],
            "conditions": {
                "deal_value": {
                    "greater_than": 10000
                }
            }
        },
        "confidence_score": 0.88,
        "usage_count": 75
    }
}


# Sample knowledge graph entities
SAMPLE_ENTITIES = {
    "customer": {
        "name": "Customer",
        "entity_type": "business_object",
        "description": "Customer entity representing individuals or organizations",
        "properties": {
            "fields": [
                {"name": "id", "type": "string", "required": True, "primary_key": True},
                {"name": "email", "type": "email", "required": True, "unique": True},
                {"name": "first_name", "type": "string", "required": True},
                {"name": "last_name", "type": "string", "required": True},
                {"name": "company", "type": "string", "required": False},
                {"name": "phone", "type": "phone", "required": False},
                {"name": "created_at", "type": "datetime", "required": True},
                {"name": "updated_at", "type": "datetime", "required": True}
            ],
            "indexes": ["email", "company"],
            "relationships": ["orders", "support_tickets"]
        },
        "confidence_score": 0.98
    },
    "order": {
        "name": "Order",
        "entity_type": "business_object",
        "description": "Order entity representing purchase transactions",
        "properties": {
            "fields": [
                {"name": "id", "type": "string", "required": True, "primary_key": True},
                {"name": "customer_id", "type": "string", "required": True, "foreign_key": "customer.id"},
                {"name": "total_amount", "type": "decimal", "required": True},
                {"name": "currency", "type": "string", "required": True, "default": "USD"},
                {"name": "status", "type": "enum", "required": True, "values": ["pending", "paid", "shipped", "delivered", "cancelled"]},
                {"name": "order_date", "type": "datetime", "required": True},
                {"name": "shipped_date", "type": "datetime", "required": False}
            ],
            "indexes": ["customer_id", "status", "order_date"],
            "relationships": ["customer", "order_items"]
        },
        "confidence_score": 0.96
    },
    "api_endpoint": {
        "name": "API Endpoint",
        "entity_type": "technical_component",
        "description": "REST API endpoint for system integration",
        "properties": {
            "fields": [
                {"name": "id", "type": "string", "required": True, "primary_key": True},
                {"name": "path", "type": "string", "required": True},
                {"name": "method", "type": "enum", "required": True, "values": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                {"name": "description", "type": "text", "required": False},
                {"name": "parameters", "type": "json", "required": False},
                {"name": "response_schema", "type": "json", "required": False},
                {"name": "rate_limit", "type": "integer", "required": False}
            ],
            "indexes": ["path", "method"],
            "relationships": ["system_connection"]
        },
        "confidence_score": 0.92
    }
}


# Sample relationships
SAMPLE_RELATIONSHIPS = {
    "customer_orders": {
        "name": "Customer Orders",
        "relationship_type": "one_to_many",
        "source_entity": "customer",
        "target_entity": "order",
        "description": "A customer can have multiple orders",
        "properties": {
            "cardinality": "1:N",
            "cascade_delete": False,
            "foreign_key": "customer_id"
        },
        "confidence_score": 0.99
    },
    "system_endpoints": {
        "name": "System API Endpoints",
        "relationship_type": "one_to_many",
        "source_entity": "system_connection",
        "target_entity": "api_endpoint",
        "description": "A system connection has multiple API endpoints",
        "properties": {
            "cardinality": "1:N",
            "cascade_delete": True,
            "foreign_key": "system_connection_id"
        },
        "confidence_score": 0.95
    }
}


# Utility functions for test data
def get_sample_timestamp() -> datetime:
    """Get a consistent timestamp for testing."""
    return datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def create_test_user_data(email: str = "test@example.com") -> Dict[str, Any]:
    """Create test user data with specified email."""
    return {
        "email": email,
        "username": email.split("@")[0],
        "full_name": "Test User",
        "hashed_password": "hashed_password_here",
        "is_active": True,
        "is_verified": True,
        "created_at": get_sample_timestamp(),
        "updated_at": get_sample_timestamp()
    }


def create_test_integration_data(name: str = "Test Integration") -> Dict[str, Any]:
    """Create test integration data with specified name."""
    return {
        "name": name,
        "description": f"Test integration: {name}",
        "integration_type": "sync",
        "status": "active",
        "source_system": "salesforce",
        "target_system": "hubspot",
        "configuration": {
            "sync_frequency": "hourly",
            "field_mappings": {
                "email": "email",
                "firstName": "first_name",
                "lastName": "last_name"
            },
            "filters": {
                "active_only": True
            }
        },
        "is_active": True,
        "created_at": get_sample_timestamp(),
        "updated_at": get_sample_timestamp()
    }


def create_test_entity_data(name: str = "Test Entity") -> Dict[str, Any]:
    """Create test entity data with specified name."""
    return {
        "name": name,
        "entity_type": "business_object",
        "description": f"Test entity: {name}",
        "properties": {
            "fields": ["id", "name", "created_at"],
            "primary_key": "id",
            "required_fields": ["name"]
        },
        "confidence_score": 0.95,
        "created_at": get_sample_timestamp(),
        "updated_at": get_sample_timestamp()
    }
