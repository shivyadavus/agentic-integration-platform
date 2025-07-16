"""
Custom exception classes for the agentic integration platform.

This module defines application-specific exceptions with proper error codes,
messages, and context for comprehensive error handling.
"""

from typing import Any, Dict, Optional


class AgenticIntegrationException(Exception):
    """Base exception for all agentic integration platform errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ) -> None:
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AgenticIntegrationException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs: Any) -> None:
        context = kwargs.pop("context", {})
        if field:
            context["field"] = field
        super().__init__(message, status_code=400, context=context, **kwargs)


class AuthenticationError(AgenticIntegrationException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(AgenticIntegrationException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", **kwargs: Any) -> None:
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(AgenticIntegrationException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs: Any) -> None:
        context = kwargs.pop("context", {})
        if resource_type:
            context["resource_type"] = resource_type
        super().__init__(message, status_code=404, context=context, **kwargs)


class ConflictError(AgenticIntegrationException):
    """Raised when a resource conflict occurs."""
    
    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, status_code=409, **kwargs)


class RateLimitError(AgenticIntegrationException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs: Any) -> None:
        super().__init__(message, status_code=429, **kwargs)


class ExternalServiceError(AgenticIntegrationException):
    """Raised when external service calls fail."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        service_error: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        context = kwargs.pop("context", {})
        status_code = kwargs.pop("status_code", 502)
        if service_name:
            context["service_name"] = service_name
        if service_error:
            context["service_error"] = service_error
        super().__init__(message, status_code=status_code, context=context, **kwargs)


class AIModelError(ExternalServiceError):
    """Raised when AI model operations fail."""

    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        context = kwargs.pop("context", {})
        if model_name:
            context["model_name"] = model_name
        if provider:
            context["provider"] = provider
        super().__init__(message, service_name="AI Model", context=context, **kwargs)


class KnowledgeGraphError(AgenticIntegrationException):
    """Raised when knowledge graph operations fail."""

    def __init__(self, message: str, operation: Optional[str] = None, **kwargs: Any) -> None:
        context = kwargs.pop("context", {})
        if operation:
            context["operation"] = operation
        super().__init__(message, context=context, **kwargs)


class CodeGenerationError(AgenticIntegrationException):
    """Raised when code generation fails."""

    def __init__(
        self,
        message: str,
        generation_stage: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        context = kwargs.pop("context", {})
        if generation_stage:
            context["generation_stage"] = generation_stage
        super().__init__(message, context=context, **kwargs)


class ValidationEngineError(AgenticIntegrationException):
    """Raised when semantic validation fails."""

    def __init__(
        self,
        message: str,
        validation_type: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        context = kwargs.pop("context", {})
        if validation_type:
            context["validation_type"] = validation_type
        super().__init__(message, context=context, **kwargs)


class IntegrationExecutionError(AgenticIntegrationException):
    """Raised when integration execution fails."""

    def __init__(
        self,
        message: str,
        integration_id: Optional[str] = None,
        execution_stage: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        context = kwargs.pop("context", {})
        if integration_id:
            context["integration_id"] = integration_id
        if execution_stage:
            context["execution_stage"] = execution_stage
        super().__init__(message, context=context, **kwargs)


class DatabaseError(AgenticIntegrationException):
    """Raised when database operations fail."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        context = kwargs.pop("context", {})
        if operation:
            context["operation"] = operation
        if table:
            context["table"] = table
        super().__init__(message, context=context, **kwargs)


class ConfigurationError(AgenticIntegrationException):
    """Raised when configuration is invalid or missing."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        context = kwargs.pop("context", {})
        if config_key:
            context["config_key"] = config_key
        super().__init__(message, context=context, **kwargs)
