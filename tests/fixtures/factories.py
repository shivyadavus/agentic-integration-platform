"""
Factory classes for creating test data using factory_boy.

This module provides factory classes for generating test instances
of domain models with realistic data.
"""

import factory
from datetime import datetime, timezone
from typing import Any, Dict

from app.models.user import User, Role, Permission
from app.models.integration import Integration, IntegrationType, IntegrationStatus
from app.models.knowledge import Entity, EntityType, Relationship, Pattern
from app.models.ai import AIModel, AIProvider, ConversationSession, Message
from app.models.system import SystemConnection, APIEndpoint, DataMapping


class UserFactory(factory.Factory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    full_name = factory.Faker("name")
    hashed_password = factory.Faker("password")
    is_active = True
    is_verified = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class RoleFactory(factory.Factory):
    """Factory for creating Role instances."""
    
    class Meta:
        model = Role
    
    name = factory.Sequence(lambda n: f"role_{n}")
    description = factory.Faker("sentence")
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class PermissionFactory(factory.Factory):
    """Factory for creating Permission instances."""
    
    class Meta:
        model = Permission
    
    name = factory.Sequence(lambda n: f"permission_{n}")
    description = factory.Faker("sentence")
    resource = factory.Faker("word")
    action = factory.Faker("word")
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class IntegrationFactory(factory.Factory):
    """Factory for creating Integration instances."""
    
    class Meta:
        model = Integration
    
    name = factory.Sequence(lambda n: f"Integration {n}")
    natural_language_spec = factory.Faker("sentence")
    integration_type = factory.Faker("random_element", elements=[t.value for t in IntegrationType])
    status = factory.Faker("random_element", elements=[s.value for s in IntegrationStatus])
    code_language = "python"
    code_version = 1
    validation_passed = False
    test_passed = False
    execution_count = 0
    success_count = 0
    error_count = 0
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class EntityFactory(factory.Factory):
    """Factory for creating Entity instances."""
    
    class Meta:
        model = Entity
    
    name = factory.Sequence(lambda n: f"Entity {n}")
    entity_type = factory.Faker("random_element", elements=[t.value for t in EntityType])
    description = factory.Faker("sentence")
    properties = factory.LazyFunction(lambda: {
        "fields": ["id", "name", "created_at"],
        "primary_key": "id"
    })
    confidence_score = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class RelationshipFactory(factory.Factory):
    """Factory for creating Relationship instances."""
    
    class Meta:
        model = Relationship
    
    name = factory.Sequence(lambda n: f"Relationship {n}")
    relationship_type = factory.Faker("word")
    description = factory.Faker("sentence")
    properties = factory.LazyFunction(lambda: {
        "cardinality": "one-to-many",
        "cascade": True
    })
    confidence_score = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class PatternFactory(factory.Factory):
    """Factory for creating Pattern instances."""
    
    class Meta:
        model = Pattern
    
    name = factory.Sequence(lambda n: f"Pattern {n}")
    pattern_type = factory.Faker("word")
    description = factory.Faker("sentence")
    template = factory.LazyFunction(lambda: {
        "trigger": "data_change",
        "action": "sync",
        "conditions": []
    })
    confidence_score = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)
    usage_count = factory.Faker("pyint", min_value=0, max_value=100)
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class AIModelFactory(factory.Factory):
    """Factory for creating AIModel instances."""
    
    class Meta:
        model = AIModel
    
    name = factory.Sequence(lambda n: f"ai_model_{n}")
    provider = factory.Faker("random_element", elements=[p.value for p in AIProvider])
    model_id = factory.Faker("word")
    description = factory.Faker("sentence")
    capabilities = factory.LazyFunction(lambda: ["text_generation", "code_generation"])
    configuration = factory.LazyFunction(lambda: {
        "max_tokens": 4000,
        "temperature": 0.7
    })
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class ConversationSessionFactory(factory.Factory):
    """Factory for creating ConversationSession instances."""
    
    class Meta:
        model = ConversationSession
    
    title = factory.Faker("sentence")
    context = factory.LazyFunction(lambda: {
        "integration_id": "test-integration",
        "user_goal": "Create data sync"
    })
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class MessageFactory(factory.Factory):
    """Factory for creating Message instances."""
    
    class Meta:
        model = Message
    
    content = factory.Faker("text")
    role = factory.Faker("random_element", elements=["user", "assistant", "system"])
    metadata = factory.LazyFunction(lambda: {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": "claude-3-sonnet"
    })
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class SystemConnectionFactory(factory.Factory):
    """Factory for creating SystemConnection instances."""
    
    class Meta:
        model = SystemConnection
    
    name = factory.Sequence(lambda n: f"System {n}")
    system_type = factory.Faker("word")
    description = factory.Faker("sentence")
    base_url = factory.Faker("url")
    authentication = factory.LazyFunction(lambda: {
        "type": "api_key",
        "key_name": "Authorization"
    })
    configuration = factory.LazyFunction(lambda: {
        "timeout": 30,
        "retry_count": 3
    })
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class APIEndpointFactory(factory.Factory):
    """Factory for creating APIEndpoint instances."""
    
    class Meta:
        model = APIEndpoint
    
    name = factory.Sequence(lambda n: f"Endpoint {n}")
    path = factory.Faker("uri_path")
    method = factory.Faker("random_element", elements=["GET", "POST", "PUT", "DELETE"])
    description = factory.Faker("sentence")
    parameters = factory.LazyFunction(lambda: {
        "query": ["limit", "offset"],
        "path": ["id"]
    })
    response_schema = factory.LazyFunction(lambda: {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"}
        }
    })
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class DataMappingFactory(factory.Factory):
    """Factory for creating DataMapping instances."""
    
    class Meta:
        model = DataMapping
    
    name = factory.Sequence(lambda n: f"Mapping {n}")
    source_field = factory.Faker("word")
    target_field = factory.Faker("word")
    transformation = factory.LazyFunction(lambda: {
        "type": "direct",
        "format": "string"
    })
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
