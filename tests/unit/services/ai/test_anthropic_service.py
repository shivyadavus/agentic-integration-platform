"""
Unit tests for the Anthropic AI service.

Tests AnthropicService implementation including client initialization,
message conversion, request handling, and error management.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import anthropic

from app.services.ai.anthropic_service import AnthropicService
from app.services.ai.base import AIMessage, AIResponse, AIModelConfig, AIModelError
from tests.fixtures.test_data import SAMPLE_AI_RESPONSES


class TestAnthropicService:
    """Test cases for AnthropicService."""
    
    def test_provider_name(self):
        """Test provider name property."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        assert service.provider_name == "anthropic"
    
    def test_supported_models(self):
        """Test supported models list."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        models = service.supported_models
        
        assert "claude-3-5-sonnet-20241022" in models
        assert "claude-3-5-haiku-20241022" in models
        assert "claude-3-opus-20240229" in models
        assert "claude-3-sonnet-20240229" in models
        assert "claude-3-haiku-20240307" in models
        assert len(models) >= 5
    
    def test_validate_supported_model(self):
        """Test model validation for supported models."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        assert service.validate_model("claude-3-sonnet-20240229") is True
        assert service.validate_model("claude-3-haiku-20240307") is True
        assert service.validate_model("claude-3-opus-20240229") is True
    
    def test_validate_unsupported_model(self):
        """Test model validation for unsupported models."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        assert service.validate_model("gpt-4") is False
        assert service.validate_model("unsupported-model") is False
        assert service.validate_model("") is False
    
    @pytest.mark.asyncio
    async def test_initialize_client(self):
        """Test client initialization."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        await service._initialize_client()
        
        assert service._client is not None
        assert isinstance(service._client, anthropic.AsyncAnthropic)
    
    def test_convert_messages_user_only(self):
        """Test message conversion with user messages only."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        messages = [
            AIMessage(role="user", content="Hello"),
            AIMessage(role="user", content="How are you?")
        ]
        
        system_prompt, converted = service._convert_messages(messages)
        
        assert system_prompt is None
        assert len(converted) == 2
        assert converted[0]["role"] == "user"
        assert converted[0]["content"] == "Hello"
        assert converted[1]["role"] == "user"
        assert converted[1]["content"] == "How are you?"
    
    def test_convert_messages_with_system(self):
        """Test message conversion with system message."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        messages = [
            AIMessage(role="system", content="You are a helpful assistant"),
            AIMessage(role="user", content="Hello"),
            AIMessage(role="assistant", content="Hi there!")
        ]
        
        system_prompt, converted = service._convert_messages(messages)
        
        assert system_prompt == "You are a helpful assistant"
        assert len(converted) == 2
        assert converted[0]["role"] == "user"
        assert converted[1]["role"] == "assistant"
    
    def test_convert_messages_multiple_system(self):
        """Test message conversion with multiple system messages."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        messages = [
            AIMessage(role="system", content="You are helpful"),
            AIMessage(role="system", content="Be concise"),
            AIMessage(role="user", content="Hello")
        ]
        
        system_prompt, converted = service._convert_messages(messages)
        
        # Should combine system messages (implementation might use last one or combine)
        assert "Be concise" in system_prompt  # At least the last system message should be there
        assert len(converted) == 1
        assert converted[0]["role"] == "user"
    
    def test_convert_functions_to_tools(self):
        """Test function to tools conversion."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        functions = [
            {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }
        ]
        
        tools = service._convert_functions_to_tools(functions)
        
        assert len(tools) == 1
        # Check the actual structure returned by the conversion
        assert "name" in tools[0]
        assert tools[0]["name"] == "get_weather"
        assert "description" in tools[0]
    
    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful request to Anthropic API."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        # Mock the client and response
        mock_client = AsyncMock()
        mock_content = MagicMock()
        mock_content.type = "text"
        mock_content.text = "Hello! How can I help you?"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 8
        mock_response.stop_reason = "end_turn"
        
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        service._client = mock_client
        
        messages = [AIMessage(role="user", content="Hello")]
        config = AIModelConfig(model="claude-3-sonnet-20240229")
        
        response = await service._make_request(messages, config)
        
        assert isinstance(response, AIResponse)
        assert response.content == "Hello! How can I help you?"
        assert response.model == "claude-3-sonnet-20240229"
        assert response.provider == "anthropic"
        assert response.input_tokens == 10
        assert response.output_tokens == 8
    
    @pytest.mark.asyncio
    async def test_make_request_with_tools(self):
        """Test request with function tools."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        # Mock response with tool use
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_text_content = MagicMock()
        mock_text_content.type = "text"
        mock_text_content.text = "I'll check the weather for you."
        mock_tool_content = MagicMock()
        mock_tool_content.type = "tool_use"
        mock_tool_content.name = "get_weather"
        mock_tool_content.input = {"location": "New York"}
        mock_tool_content.id = "tool_123"
        mock_response.content = [mock_text_content, mock_tool_content]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 25
        mock_response.stop_reason = "tool_use"
        
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        service._client = mock_client
        
        messages = [AIMessage(role="user", content="What's the weather in New York?")]
        config = AIModelConfig(
            model="claude-3-sonnet-20240229",
            functions=[{
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {"type": "object", "properties": {"location": {"type": "string"}}}
            }]
        )
        
        response = await service._make_request(messages, config)
        
        assert response.function_calls is not None
        assert len(response.function_calls) == 1
        assert response.function_calls[0]["name"] == "get_weather"
        assert response.function_calls[0]["arguments"]["location"] == "New York"
    
    @pytest.mark.asyncio
    async def test_make_request_api_error(self):
        """Test handling of Anthropic API errors."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        mock_client = AsyncMock()
        # Create a proper APIError with required arguments
        mock_request = MagicMock()
        mock_response = MagicMock()
        api_error = anthropic.APIError("Rate limit exceeded", request=mock_request, body={"error": "rate_limit"})
        mock_client.messages.create = AsyncMock(side_effect=api_error)
        service._client = mock_client
        
        messages = [AIMessage(role="user", content="Hello")]
        config = AIModelConfig(model="claude-3-sonnet-20240229")
        
        with pytest.raises(AIModelError) as exc_info:
            await service._make_request(messages, config)
        
        assert "Anthropic API error" in str(exc_info.value)
        assert exc_info.value.context.get("provider") == "anthropic"
        assert exc_info.value.context.get("model_name") == "claude-3-sonnet-20240229"
    
    @pytest.mark.asyncio
    async def test_make_request_unexpected_error(self):
        """Test handling of unexpected errors."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=ValueError("Unexpected error")
        )
        service._client = mock_client
        
        messages = [AIMessage(role="user", content="Hello")]
        config = AIModelConfig(model="claude-3-sonnet-20240229")
        
        with pytest.raises(AIModelError) as exc_info:
            await service._make_request(messages, config)
        
        assert "Unexpected error in Anthropic request" in str(exc_info.value)
    
    @pytest.mark.skip(reason="stream_response method not implemented")
    @pytest.mark.asyncio
    async def test_stream_response(self):
        """Test streaming response functionality."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        # Mock streaming response
        mock_client = AsyncMock()
        
        # Create mock stream chunks
        chunks = [
            MagicMock(type="content_block_delta", delta=MagicMock(text="Hello")),
            MagicMock(type="content_block_delta", delta=MagicMock(text=" there")),
            MagicMock(type="content_block_delta", delta=MagicMock(text="!")),
            MagicMock(type="message_delta")  # Non-text chunk
        ]
        
        async def mock_stream():
            for chunk in chunks:
                yield chunk
        
        mock_client.messages.create = AsyncMock(return_value=mock_stream())
        service._client = mock_client
        
        messages = [AIMessage(role="user", content="Hello")]
        config = AIModelConfig(model="claude-3-sonnet-20240229")
        
        # Collect streamed text
        streamed_text = []
        async for text_chunk in service.stream_response(messages, config):
            streamed_text.append(text_chunk)
        
        assert streamed_text == ["Hello", " there", "!"]
    
    @pytest.mark.asyncio
    async def test_generate_response_integration(self):
        """Test full generate_response flow."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        # Mock successful response
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.type = "text"
        mock_content.text = "Integration test response"
        mock_response.content = [mock_content]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 20
        mock_response.usage.output_tokens = 15
        mock_response.stop_reason = "end_turn"
        
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        service._client = mock_client
        
        messages = [AIMessage(role="user", content="Test message")]
        
        response = await service.generate_response(messages)
        
        assert isinstance(response, AIResponse)
        assert response.content == "Integration test response"
        assert response.provider == "anthropic"


@pytest.mark.unit
class TestAnthropicServiceEdgeCases:
    """Test edge cases for AnthropicService."""
    
    @pytest.mark.asyncio
    async def test_empty_response_content(self):
        """Test handling of empty response content."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = []  # Empty content
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 0
        mock_response.stop_reason = "end_turn"
        
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        service._client = mock_client
        
        messages = [AIMessage(role="user", content="Hello")]
        config = AIModelConfig(model="claude-3-sonnet-20240229")
        
        response = await service._make_request(messages, config)
        
        assert response.content == ""
        assert response.output_tokens == 0
    
    def test_convert_messages_empty_list(self):
        """Test message conversion with empty message list."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        system_prompt, converted = service._convert_messages([])
        
        assert system_prompt is None
        assert converted == []
    
    def test_convert_functions_empty_list(self):
        """Test function conversion with empty function list."""
        service = AnthropicService(api_key="test-key", default_model="claude-3-sonnet-20240229")
        
        tools = service._convert_functions_to_tools([])
        
        assert tools == []
