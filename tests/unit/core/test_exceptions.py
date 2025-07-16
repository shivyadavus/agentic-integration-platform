"""
Unit tests for custom exception classes.

Tests exception initialization, error codes, status codes, context handling,
and inheritance hierarchy.
"""

import pytest

from app.core.exceptions import (
    AgenticIntegrationException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConfigurationError,
    ExternalServiceError,
    IntegrationExecutionError,
    AIModelError,
    KnowledgeGraphError,
)


class TestAgenticIntegrationException:
    """Test cases for the base exception class."""
    
    def test_basic_exception_creation(self):
        """Test basic exception creation with message only."""
        exc = AgenticIntegrationException("Test error message")
        
        assert str(exc) == "Test error message"
        assert exc.message == "Test error message"
        assert exc.error_code == "AgenticIntegrationException"
        assert exc.context == {}
        assert exc.status_code == 500
    
    def test_exception_with_error_code(self):
        """Test exception creation with custom error code."""
        exc = AgenticIntegrationException(
            "Test error",
            error_code="CUSTOM_ERROR"
        )
        
        assert exc.error_code == "CUSTOM_ERROR"
        assert exc.message == "Test error"
    
    def test_exception_with_context(self):
        """Test exception creation with context."""
        context = {"user_id": "123", "operation": "data_sync"}
        exc = AgenticIntegrationException(
            "Test error",
            context=context
        )
        
        assert exc.context == context
        assert exc.context["user_id"] == "123"
        assert exc.context["operation"] == "data_sync"
    
    def test_exception_with_status_code(self):
        """Test exception creation with custom status code."""
        exc = AgenticIntegrationException(
            "Test error",
            status_code=422
        )
        
        assert exc.status_code == 422
    
    def test_exception_with_all_parameters(self):
        """Test exception creation with all parameters."""
        context = {"field": "email", "value": "invalid"}
        exc = AgenticIntegrationException(
            "Validation failed",
            error_code="VALIDATION_ERROR",
            context=context,
            status_code=400
        )
        
        assert exc.message == "Validation failed"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.context == context
        assert exc.status_code == 400


class TestValidationError:
    """Test cases for ValidationError."""
    
    def test_basic_validation_error(self):
        """Test basic validation error creation."""
        exc = ValidationError("Invalid input")
        
        assert exc.message == "Invalid input"
        assert exc.error_code == "ValidationError"
        assert exc.status_code == 400
    
    def test_validation_error_with_field(self):
        """Test validation error with field information."""
        exc = ValidationError("Email is required", field="email")
        
        assert exc.message == "Email is required"
        assert exc.context["field"] == "email"
        assert exc.status_code == 400
    
    def test_validation_error_with_context(self):
        """Test validation error with additional context."""
        context = {"min_length": 8, "actual_length": 5}
        exc = ValidationError(
            "Password too short",
            field="password",
            context=context
        )
        
        assert exc.context["field"] == "password"
        assert exc.context["min_length"] == 8
        assert exc.context["actual_length"] == 5


class TestAuthenticationError:
    """Test cases for AuthenticationError."""
    
    def test_default_authentication_error(self):
        """Test default authentication error."""
        exc = AuthenticationError()
        
        assert exc.message == "Authentication failed"
        assert exc.error_code == "AuthenticationError"
        assert exc.status_code == 401
    
    def test_custom_authentication_error(self):
        """Test authentication error with custom message."""
        exc = AuthenticationError("Invalid API key")
        
        assert exc.message == "Invalid API key"
        assert exc.status_code == 401
    
    def test_authentication_error_with_context(self):
        """Test authentication error with context."""
        context = {"provider": "oauth2", "reason": "token_expired"}
        exc = AuthenticationError(
            "Token has expired",
            context=context
        )
        
        assert exc.context["provider"] == "oauth2"
        assert exc.context["reason"] == "token_expired"


class TestAuthorizationError:
    """Test cases for AuthorizationError."""
    
    def test_default_authorization_error(self):
        """Test default authorization error."""
        exc = AuthorizationError()
        
        assert exc.message == "Access denied"
        assert exc.error_code == "AuthorizationError"
        assert exc.status_code == 403
    
    def test_custom_authorization_error(self):
        """Test authorization error with custom message."""
        exc = AuthorizationError("Insufficient permissions")
        
        assert exc.message == "Insufficient permissions"
        assert exc.status_code == 403
    
    def test_authorization_error_with_context(self):
        """Test authorization error with context."""
        context = {"required_role": "admin", "user_role": "user"}
        exc = AuthorizationError(
            "Admin role required",
            context=context
        )
        
        assert exc.context["required_role"] == "admin"
        assert exc.context["user_role"] == "user"


class TestNotFoundError:
    """Test cases for NotFoundError."""
    
    def test_basic_not_found_error(self):
        """Test basic not found error."""
        exc = NotFoundError("Resource not found")
        
        assert exc.message == "Resource not found"
        assert exc.error_code == "NotFoundError"
        assert exc.status_code == 404
    
    def test_not_found_error_with_resource_type(self):
        """Test not found error with resource type."""
        exc = NotFoundError("User not found", resource_type="user")
        
        assert exc.message == "User not found"
        assert exc.context["resource_type"] == "user"
        assert exc.status_code == 404
    
    def test_not_found_error_with_context(self):
        """Test not found error with additional context."""
        context = {"id": "123", "table": "users"}
        exc = NotFoundError(
            "User not found",
            resource_type="user",
            context=context
        )
        
        assert exc.context["resource_type"] == "user"
        assert exc.context["id"] == "123"
        assert exc.context["table"] == "users"


class TestConfigurationError:
    """Test cases for ConfigurationError."""
    
    def test_configuration_error(self):
        """Test configuration error."""
        exc = ConfigurationError("Invalid configuration")
        
        assert exc.message == "Invalid configuration"
        assert exc.error_code == "ConfigurationError"
        assert exc.status_code == 500
    
    def test_configuration_error_with_setting(self):
        """Test configuration error with setting information."""
        exc = ConfigurationError(
            "Database URL is invalid",
            config_key="database_url"
        )

        assert exc.context["config_key"] == "database_url"


class TestExternalServiceError:
    """Test cases for ExternalServiceError."""
    
    def test_external_service_error(self):
        """Test external service error."""
        exc = ExternalServiceError("Service unavailable")
        
        assert exc.message == "Service unavailable"
        assert exc.error_code == "ExternalServiceError"
        assert exc.status_code == 502
    
    def test_external_service_error_with_service(self):
        """Test external service error with service information."""
        exc = ExternalServiceError(
            "API rate limit exceeded",
            service_name="anthropic",
            status_code=503
        )

        assert exc.context["service_name"] == "anthropic"
        assert exc.status_code == 503


class TestIntegrationExecutionError:
    """Test cases for IntegrationExecutionError."""

    def test_integration_execution_error(self):
        """Test integration execution error."""
        exc = IntegrationExecutionError("Integration failed")

        assert exc.message == "Integration failed"
        assert exc.error_code == "IntegrationExecutionError"
        assert exc.status_code == 500

    def test_integration_execution_error_with_integration_id(self):
        """Test integration execution error with integration ID."""
        exc = IntegrationExecutionError(
            "Sync failed",
            integration_id="int_123"
        )

        assert exc.context["integration_id"] == "int_123"


class TestAIModelError:
    """Test cases for AIModelError."""

    def test_ai_model_error(self):
        """Test AI model error."""
        exc = AIModelError("AI model error")

        assert exc.message == "AI model error"
        assert exc.error_code == "AIModelError"
        assert exc.status_code == 502  # Inherits from ExternalServiceError

    def test_ai_model_error_with_provider(self):
        """Test AI model error with provider information."""
        exc = AIModelError(
            "Model not available",
            provider="openai",
            model_name="gpt-4"
        )

        assert exc.context["provider"] == "openai"
        assert exc.context["model_name"] == "gpt-4"


class TestKnowledgeGraphError:
    """Test cases for KnowledgeGraphError."""
    
    def test_knowledge_graph_error(self):
        """Test knowledge graph error."""
        exc = KnowledgeGraphError("Graph operation failed")
        
        assert exc.message == "Graph operation failed"
        assert exc.error_code == "KnowledgeGraphError"
        assert exc.status_code == 500
    
    def test_knowledge_graph_error_with_operation(self):
        """Test knowledge graph error with operation information."""
        exc = KnowledgeGraphError(
            "Failed to create relationship",
            operation="create_relationship",
            context={"entity_id": "ent_123"}
        )

        assert exc.context["operation"] == "create_relationship"
        assert exc.context["entity_id"] == "ent_123"


@pytest.mark.unit
class TestExceptionInheritance:
    """Test cases for exception inheritance and polymorphism."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from base exception."""
        exceptions = [
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            NotFoundError("test"),
            ConfigurationError("test"),
            ExternalServiceError("test"),
            IntegrationExecutionError("test"),
            AIModelError("test"),
            KnowledgeGraphError("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AgenticIntegrationException)
            assert isinstance(exc, Exception)
    
    def test_exception_polymorphism(self):
        """Test exception polymorphism in exception handling."""
        exceptions = [
            ValidationError("validation failed"),
            AuthenticationError("auth failed"),
            NotFoundError("not found"),
        ]
        
        for exc in exceptions:
            # Should be able to handle as base exception
            try:
                raise exc
            except AgenticIntegrationException as e:
                assert hasattr(e, 'message')
                assert hasattr(e, 'error_code')
                assert hasattr(e, 'status_code')
                assert hasattr(e, 'context')
    
    def test_exception_error_codes_are_unique(self):
        """Test that different exception types have different error codes."""
        exceptions = [
            ValidationError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            NotFoundError("test"),
        ]
        
        error_codes = [exc.error_code for exc in exceptions]
        assert len(error_codes) == len(set(error_codes))  # All unique
