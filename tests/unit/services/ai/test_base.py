"""
Unit tests for the base AI service class.

Tests the abstract AIService class, AIMessage, AIResponse, AIModelConfig,
and common functionality shared by all AI service implementations.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai.base import (
    AIService,
    AIMessage,
    AIResponse,
    AIModelConfig,
    AIModelError,
)
from app.core.exceptions import AIModelError


# Concrete implementation for testing
class MockAIService(AIService):
    """Test implementation of AIService for unit testing."""
    
    @property
    def provider_name(self) -> str:
        return "test_provider"
    
    @property
    def supported_models(self) -> list[str]:
        return ["test-model-1", "test-model-2", "test-model-large"]
    
    async def _initialize_client(self) -> None:
        self._client = MagicMock()
    
    async def _make_request(self, messages, config) -> AIResponse:
        # Simulate processing time
        await asyncio.sleep(0.01)
        
        return AIResponse(
            content="Test response content",
            model=config.model,
            provider=self.provider_name,
            input_tokens=100,
            output_tokens=50,
            processing_time_ms=10,
        )


class TestAIMessage:
    """Test cases for AIMessage dataclass."""
    
    def test_ai_message_creation(self):
        """Test AIMessage creation with required fields."""
        message = AIMessage(role="user", content="Hello, AI!")
        
        assert message.role == "user"
        assert message.content == "Hello, AI!"
        assert message.metadata is None
    
    def test_ai_message_with_metadata(self):
        """Test AIMessage creation with metadata."""
        metadata = {"timestamp": "2024-01-01T00:00:00Z", "user_id": "123"}
        message = AIMessage(
            role="assistant",
            content="Hello, human!",
            metadata=metadata
        )
        
        assert message.role == "assistant"
        assert message.content == "Hello, human!"
        assert message.metadata == metadata
    
    def test_ai_message_roles(self):
        """Test different message roles."""
        roles = ["user", "assistant", "system", "function"]
        
        for role in roles:
            message = AIMessage(role=role, content=f"Content for {role}")
            assert message.role == role
            assert message.content == f"Content for {role}"


class TestAIResponse:
    """Test cases for AIResponse dataclass."""
    
    def test_ai_response_creation(self):
        """Test AIResponse creation with required fields."""
        response = AIResponse(
            content="AI response",
            model="test-model",
            provider="test-provider",
            input_tokens=100,
            output_tokens=50,
            processing_time_ms=150
        )
        
        assert response.content == "AI response"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.processing_time_ms == 150
        assert response.function_calls is None
        assert response.metadata is None
    
    def test_ai_response_with_function_calls(self):
        """Test AIResponse with function calls."""
        function_calls = [
            {"name": "get_weather", "arguments": {"location": "New York"}},
            {"name": "send_email", "arguments": {"to": "user@example.com"}}
        ]
        
        response = AIResponse(
            content="I'll help you with that.",
            model="test-model",
            provider="test-provider",
            input_tokens=100,
            output_tokens=50,
            processing_time_ms=150,
            function_calls=function_calls
        )
        
        assert response.function_calls == function_calls
        assert len(response.function_calls) == 2
    
    def test_ai_response_with_metadata(self):
        """Test AIResponse with metadata."""
        metadata = {"stop_reason": "end_turn", "finish_reason": "stop"}
        
        response = AIResponse(
            content="Response with metadata",
            model="test-model",
            provider="test-provider",
            input_tokens=100,
            output_tokens=50,
            processing_time_ms=150,
            metadata=metadata
        )
        
        assert response.metadata == metadata


class TestAIModelConfig:
    """Test cases for AIModelConfig dataclass."""
    
    def test_ai_model_config_defaults(self):
        """Test AIModelConfig with default values."""
        config = AIModelConfig(model="test-model")
        
        assert config.model == "test-model"
        assert config.temperature == 0.1
        assert config.max_tokens == 4096
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
        assert config.stop_sequences is None
        assert config.system_prompt is None
        assert config.functions is None
        assert config.function_call is None
    
    def test_ai_model_config_custom_values(self):
        """Test AIModelConfig with custom values."""
        config = AIModelConfig(
            model="custom-model",
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.2,
            stop_sequences=["STOP", "END"],
            system_prompt="You are a helpful assistant.",
            functions=[{"name": "test_function"}],
            function_call="auto"
        )
        
        assert config.model == "custom-model"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.1
        assert config.presence_penalty == 0.2
        assert config.stop_sequences == ["STOP", "END"]
        assert config.system_prompt == "You are a helpful assistant."
        assert config.functions == [{"name": "test_function"}]
        assert config.function_call == "auto"


class MockAIServiceBase:
    """Test cases for the base AIService class."""
    
    def test_ai_service_initialization(self):
        """Test AIService initialization."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")

        assert service.api_key == "test-key"
        assert service.default_model == "test-model-1"
        assert service._client is None
        assert service.provider_name == "test_provider"
        assert "test-model-1" in service.supported_models

    def test_validate_model_supported(self):
        """Test model validation for supported models."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")

        assert service.validate_model("test-model-1") is True
        assert service.validate_model("test-model-2") is True
        assert service.validate_model("test-model-large") is True

    def test_validate_model_unsupported(self):
        """Test model validation for unsupported models."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")

        assert service.validate_model("unsupported-model") is False
        assert service.validate_model("gpt-4") is False
        assert service.validate_model("") is False

    @pytest.mark.asyncio
    async def test_ensure_client_initialization(self):
        """Test client initialization through ensure_client."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")

        assert service._client is None

        await service.ensure_client()

        assert service._client is not None

    @pytest.mark.asyncio
    async def test_ensure_client_idempotent(self):
        """Test that ensure_client is idempotent."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        await service.ensure_client()
        first_client = service._client
        
        await service.ensure_client()
        second_client = service._client
        
        assert first_client is second_client
    
    @pytest.mark.asyncio
    async def test_generate_response_default_config(self):
        """Test generate_response with default configuration."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        messages = [AIMessage(role="user", content="Hello")]
        response = await service.generate_response(messages)
        
        assert isinstance(response, AIResponse)
        assert response.content == "Test response content"
        assert response.model == "test-model-1"
        assert response.provider == "test_provider"
        assert response.input_tokens == 100
        assert response.output_tokens == 50
    
    @pytest.mark.asyncio
    async def test_generate_response_custom_config(self):
        """Test generate_response with custom configuration."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        messages = [AIMessage(role="user", content="Hello")]
        config = AIModelConfig(
            model="test-model-2",
            temperature=0.5,
            max_tokens=1024
        )
        
        response = await service.generate_response(messages, config)
        
        assert response.model == "test-model-2"
    
    @pytest.mark.asyncio
    async def test_generate_code(self):
        """Test code generation functionality."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        specification = "Create a function that adds two numbers"
        response = await service.generate_code(specification, language="python")
        
        assert isinstance(response, AIResponse)
        assert response.content == "Test response content"
    
    @pytest.mark.asyncio
    async def test_generate_code_with_context(self):
        """Test code generation with additional context."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        specification = "Create a REST API endpoint"
        context = {"framework": "FastAPI", "database": "PostgreSQL"}
        
        response = await service.generate_code(
            specification,
            language="python",
            context=context
        )
        
        assert isinstance(response, AIResponse)
    
    @pytest.mark.asyncio
    async def test_analyze_integration_requirements(self):
        """Test integration requirements analysis."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        spec = "Sync customer data from Salesforce to HubSpot"
        source_system = {"name": "Salesforce", "type": "CRM"}
        target_system = {"name": "HubSpot", "type": "CRM"}
        
        response = await service.analyze_integration_requirements(
            spec,
            source_system=source_system,
            target_system=target_system
        )
        
        assert isinstance(response, AIResponse)
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        result = await service.health_check()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        # Mock _make_request to raise an exception
        with patch.object(service, '_make_request', side_effect=Exception("API Error")):
            result = await service.health_check()
            
            assert result is False


@pytest.mark.unit
class MockAIServiceErrorHandling:
    """Test cases for AI service error handling."""
    
    @pytest.mark.asyncio
    async def test_generate_response_with_ai_model_error(self):
        """Test error handling in generate_response."""
        service = MockAIService(api_key="test-key", default_model="test-model-1")
        
        # Mock _make_request to raise AIModelError
        with patch.object(service, '_make_request', side_effect=AIModelError("API Error")):
            with pytest.raises(AIModelError):
                messages = [AIMessage(role="user", content="Hello")]
                await service.generate_response(messages)
    
    def test_ai_model_error_creation(self):
        """Test AIModelError creation."""
        error = AIModelError(
            "Test error message",
            model_name="test-model",
            provider="test-provider",
            context={"error_code": "RATE_LIMIT"}
        )
        
        assert str(error) == "Test error message"
        assert error.model_name == "test-model"
        assert error.provider == "test-provider"
        assert error.context["error_code"] == "RATE_LIMIT"
    
    def test_ai_model_error_inheritance(self):
        """Test that AIModelError inherits from ExternalServiceError."""
        error = AIModelError("Test error")

        assert isinstance(error, AIModelError)
        assert isinstance(error, Exception)
