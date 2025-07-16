"""
Anthropic Claude AI service implementation.

This module provides integration with Anthropic's Claude models
for the agentic integration platform.
"""

import time
from typing import List, Optional, AsyncGenerator

import anthropic
from anthropic.types import Message as AnthropicMessage

from app.services.ai.base import AIService, AIMessage, AIResponse, AIModelConfig
from app.core.exceptions import AIModelError


class AnthropicService(AIService):
    """
    Anthropic Claude AI service implementation.
    
    Provides integration with Claude models for natural language processing,
    code generation, and integration analysis.
    """
    
    # Supported Claude models
    SUPPORTED_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022", 
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "anthropic"
    
    @property
    def supported_models(self) -> List[str]:
        """Get list of supported models."""
        return self.SUPPORTED_MODELS
    
    async def _initialize_client(self) -> None:
        """Initialize the Anthropic client."""
        try:
            self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            self.logger.info("Anthropic client initialized successfully")
        except Exception as e:
            raise AIModelError(
                f"Failed to initialize Anthropic client: {str(e)}",
                provider="anthropic"
            )
    
    def _convert_messages(self, messages: List[AIMessage]) -> tuple[Optional[str], List[dict]]:
        """
        Convert AIMessage objects to Anthropic format.
        
        Args:
            messages: List of AIMessage objects
            
        Returns:
            tuple: (system_prompt, converted_messages)
        """
        system_prompt = None
        converted_messages = []
        
        for message in messages:
            if message.role == "system":
                # Anthropic handles system prompts separately
                system_prompt = message.content
            elif message.role in ["user", "assistant"]:
                converted_messages.append({
                    "role": message.role,
                    "content": message.content
                })
            elif message.role == "function":
                # Handle function calls (tool use in Anthropic)
                converted_messages.append({
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": message.function_name or "function_call",
                            "name": message.function_name,
                            "input": message.function_arguments or {}
                        }
                    ]
                })
        
        return system_prompt, converted_messages
    
    async def _make_request(
        self,
        messages: List[AIMessage],
        config: AIModelConfig
    ) -> AIResponse:
        """
        Make a request to the Anthropic API.
        
        Args:
            messages: List of messages in the conversation
            config: Model configuration
            
        Returns:
            AIResponse: The model's response
        """
        start_time = time.time()
        
        try:
            system_prompt, converted_messages = self._convert_messages(messages)
            
            # Prepare request parameters
            request_params = {
                "model": config.model,
                "messages": converted_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
            
            # Add system prompt if present
            if system_prompt:
                request_params["system"] = system_prompt
            
            # Add stop sequences if specified
            if config.stop_sequences:
                request_params["stop_sequences"] = config.stop_sequences
            
            # Add tools/functions if specified
            if config.functions:
                request_params["tools"] = self._convert_functions_to_tools(config.functions)
                if config.function_call:
                    request_params["tool_choice"] = {"type": "tool", "name": config.function_call}
            
            # Make the API request
            response: AnthropicMessage = await self._client.messages.create(**request_params)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Extract content
            content = ""
            function_calls = []
            
            for content_block in response.content:
                if content_block.type == "text":
                    content += content_block.text
                elif content_block.type == "tool_use":
                    function_calls.append({
                        "name": content_block.name,
                        "arguments": content_block.input,
                        "id": content_block.id
                    })
            
            return AIResponse(
                content=content,
                model=response.model,
                provider=self.provider_name,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                processing_time_ms=processing_time,
                function_calls=function_calls if function_calls else None,
                metadata={
                    "stop_reason": response.stop_reason,
                    "stop_sequence": getattr(response, "stop_sequence", None)
                }
            )
            
        except anthropic.APIError as e:
            raise AIModelError(
                f"Anthropic API error: {str(e)}",
                model_name=config.model,
                provider=self.provider_name,
                context={"error_type": type(e).__name__}
            )
        except Exception as e:
            raise AIModelError(
                f"Unexpected error in Anthropic request: {str(e)}",
                model_name=config.model,
                provider=self.provider_name
            )
    
    async def generate_streaming_response(
        self,
        messages: List[AIMessage],
        config: Optional[AIModelConfig] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from Claude.
        
        Args:
            messages: List of messages in the conversation
            config: Model configuration
            
        Yields:
            str: Chunks of the response content
        """
        await self.ensure_client()
        
        if config is None:
            config = AIModelConfig(model=self.default_model)
        
        try:
            system_prompt, converted_messages = self._convert_messages(messages)
            
            request_params = {
                "model": config.model,
                "messages": converted_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "stream": True,
            }
            
            if system_prompt:
                request_params["system"] = system_prompt
            
            if config.stop_sequences:
                request_params["stop_sequences"] = config.stop_sequences
            
            stream = await self._client.messages.create(**request_params)

            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    if hasattr(chunk.delta, "text"):
                        yield chunk.delta.text
                elif chunk.type == "message_delta":
                    # Handle message-level deltas if needed
                    pass
            
        except anthropic.APIError as e:
            raise AIModelError(
                f"Anthropic streaming API error: {str(e)}",
                model_name=config.model,
                provider=self.provider_name
            )
        except Exception as e:
            raise AIModelError(
                f"Unexpected error in Anthropic streaming: {str(e)}",
                model_name=config.model,
                provider=self.provider_name
            )
    
    def _convert_functions_to_tools(self, functions: List[dict]) -> List[dict]:
        """
        Convert OpenAI-style function definitions to Anthropic tools.
        
        Args:
            functions: List of function definitions
            
        Returns:
            List[dict]: Anthropic tool definitions
        """
        tools = []
        
        for func in functions:
            tool = {
                "name": func["name"],
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {})
            }
            tools.append(tool)
        
        return tools
    
    async def get_model_info(self, model: str) -> dict:
        """
        Get information about a specific model.
        
        Args:
            model: Model name
            
        Returns:
            dict: Model information
        """
        model_info = {
            "claude-3-5-sonnet-20241022": {
                "max_tokens": 200000,
                "context_window": 200000,
                "supports_vision": True,
                "supports_tools": True,
                "cost_per_1k_input_tokens": 0.003,
                "cost_per_1k_output_tokens": 0.015,
            },
            "claude-3-5-haiku-20241022": {
                "max_tokens": 200000,
                "context_window": 200000,
                "supports_vision": True,
                "supports_tools": True,
                "cost_per_1k_input_tokens": 0.0008,
                "cost_per_1k_output_tokens": 0.004,
            },
            "claude-3-opus-20240229": {
                "max_tokens": 200000,
                "context_window": 200000,
                "supports_vision": True,
                "supports_tools": True,
                "cost_per_1k_input_tokens": 0.015,
                "cost_per_1k_output_tokens": 0.075,
            },
        }
        
        return model_info.get(model, {
            "max_tokens": 200000,
            "context_window": 200000,
            "supports_vision": False,
            "supports_tools": False,
        })
