"""
OpenAI GPT AI service implementation.

This module provides integration with OpenAI's GPT models
for the agentic integration platform.
"""

import time
from typing import List, Optional, AsyncGenerator

import openai
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from app.services.ai.base import AIService, AIMessage, AIResponse, AIModelConfig
from app.core.exceptions import AIModelError


class OpenAIService(AIService):
    """
    OpenAI GPT AI service implementation.
    
    Provides integration with GPT models for natural language processing,
    code generation, and integration analysis.
    """
    
    # Supported GPT models
    SUPPORTED_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    ]
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"
    
    @property
    def supported_models(self) -> List[str]:
        """Get list of supported models."""
        return self.SUPPORTED_MODELS
    
    async def _initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        try:
            self._client = openai.AsyncOpenAI(api_key=self.api_key)
            self.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            raise AIModelError(
                f"Failed to initialize OpenAI client: {str(e)}",
                provider="openai"
            )
    
    def _convert_messages(self, messages: List[AIMessage]) -> List[dict]:
        """
        Convert AIMessage objects to OpenAI format.
        
        Args:
            messages: List of AIMessage objects
            
        Returns:
            List[dict]: Converted messages in OpenAI format
        """
        converted_messages = []
        
        for message in messages:
            if message.role in ["user", "assistant", "system"]:
                converted_messages.append({
                    "role": message.role,
                    "content": message.content
                })
            elif message.role == "function":
                # Handle function call responses
                converted_messages.append({
                    "role": "function",
                    "name": message.function_name,
                    "content": message.content
                })
            elif message.role == "tool":
                # Handle tool call responses
                converted_messages.append({
                    "role": "tool",
                    "tool_call_id": message.metadata.get("tool_call_id") if message.metadata else None,
                    "content": message.content
                })
        
        return converted_messages
    
    async def _make_request(
        self,
        messages: List[AIMessage],
        config: AIModelConfig
    ) -> AIResponse:
        """
        Make a request to the OpenAI API.
        
        Args:
            messages: List of messages in the conversation
            config: Model configuration
            
        Returns:
            AIResponse: The model's response
        """
        start_time = time.time()
        
        try:
            converted_messages = self._convert_messages(messages)
            
            # Prepare request parameters
            request_params = {
                "model": config.model,
                "messages": converted_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
            }
            
            # Add stop sequences if specified
            if config.stop_sequences:
                request_params["stop"] = config.stop_sequences
            
            # Add functions/tools if specified
            if config.functions:
                if self._supports_tools(config.model):
                    request_params["tools"] = self._convert_functions_to_tools(config.functions)
                    if config.function_call:
                        if config.function_call == "auto":
                            request_params["tool_choice"] = "auto"
                        elif config.function_call == "none":
                            request_params["tool_choice"] = "none"
                        else:
                            request_params["tool_choice"] = {
                                "type": "function",
                                "function": {"name": config.function_call}
                            }
                else:
                    # Fallback to legacy functions for older models
                    request_params["functions"] = config.functions
                    if config.function_call:
                        request_params["function_call"] = config.function_call
            
            # Make the API request
            response: ChatCompletion = await self._client.chat.completions.create(**request_params)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Extract content and function calls
            message = response.choices[0].message
            content = message.content or ""
            function_calls = []
            
            # Handle tool calls (new format)
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    function_calls.append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    })
            
            # Handle function calls (legacy format)
            elif hasattr(message, "function_call") and message.function_call:
                function_calls.append({
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                })
            
            return AIResponse(
                content=content,
                model=response.model,
                provider=self.provider_name,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                processing_time_ms=processing_time,
                function_calls=function_calls if function_calls else None,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "system_fingerprint": getattr(response, "system_fingerprint", None)
                }
            )
            
        except openai.APIError as e:
            raise AIModelError(
                f"OpenAI API error: {str(e)}",
                model_name=config.model,
                provider=self.provider_name,
                context={"error_type": type(e).__name__}
            )
        except Exception as e:
            raise AIModelError(
                f"Unexpected error in OpenAI request: {str(e)}",
                model_name=config.model,
                provider=self.provider_name
            )
    
    async def generate_streaming_response(
        self,
        messages: List[AIMessage],
        config: Optional[AIModelConfig] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from GPT.
        
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
            converted_messages = self._convert_messages(messages)
            
            request_params = {
                "model": config.model,
                "messages": converted_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
                "stream": True,
            }
            
            if config.stop_sequences:
                request_params["stop"] = config.stop_sequences
            
            if config.functions:
                if self._supports_tools(config.model):
                    request_params["tools"] = self._convert_functions_to_tools(config.functions)
                else:
                    request_params["functions"] = config.functions
            
            stream = await self._client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
        except openai.APIError as e:
            raise AIModelError(
                f"OpenAI streaming API error: {str(e)}",
                model_name=config.model,
                provider=self.provider_name
            )
        except Exception as e:
            raise AIModelError(
                f"Unexpected error in OpenAI streaming: {str(e)}",
                model_name=config.model,
                provider=self.provider_name
            )
    
    def _supports_tools(self, model: str) -> bool:
        """
        Check if a model supports the new tools format.
        
        Args:
            model: Model name
            
        Returns:
            bool: True if model supports tools
        """
        # Models that support the new tools format
        tools_models = [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
        ]
        
        return any(model.startswith(supported) for supported in tools_models)
    
    def _convert_functions_to_tools(self, functions: List[dict]) -> List[dict]:
        """
        Convert function definitions to OpenAI tools format.
        
        Args:
            functions: List of function definitions
            
        Returns:
            List[dict]: OpenAI tool definitions
        """
        tools = []
        
        for func in functions:
            tool = {
                "type": "function",
                "function": func
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
            "gpt-4o": {
                "max_tokens": 128000,
                "context_window": 128000,
                "supports_vision": True,
                "supports_tools": True,
                "cost_per_1k_input_tokens": 0.005,
                "cost_per_1k_output_tokens": 0.015,
            },
            "gpt-4o-mini": {
                "max_tokens": 128000,
                "context_window": 128000,
                "supports_vision": True,
                "supports_tools": True,
                "cost_per_1k_input_tokens": 0.00015,
                "cost_per_1k_output_tokens": 0.0006,
            },
            "gpt-4-turbo": {
                "max_tokens": 128000,
                "context_window": 128000,
                "supports_vision": True,
                "supports_tools": True,
                "cost_per_1k_input_tokens": 0.01,
                "cost_per_1k_output_tokens": 0.03,
            },
            "gpt-3.5-turbo": {
                "max_tokens": 16385,
                "context_window": 16385,
                "supports_vision": False,
                "supports_tools": True,
                "cost_per_1k_input_tokens": 0.0005,
                "cost_per_1k_output_tokens": 0.0015,
            },
        }
        
        return model_info.get(model, {
            "max_tokens": 4096,
            "context_window": 4096,
            "supports_vision": False,
            "supports_tools": False,
        })
