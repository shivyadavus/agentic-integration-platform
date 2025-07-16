"""
Base AI service interface for the agentic integration platform.

This module defines the abstract base class for AI service implementations,
providing a consistent interface for different AI providers.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass

from app.core.exceptions import AIModelError
from app.core.logging import LoggerMixin


@dataclass
class AIMessage:
    """Represents a message in an AI conversation."""
    
    role: str  # "user", "assistant", "system", "function"
    content: str
    function_name: Optional[str] = None
    function_arguments: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """Represents a response from an AI model."""
    
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    processing_time_ms: float
    function_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.input_tokens + self.output_tokens


@dataclass
class AIModelConfig:
    """Configuration for AI model requests."""
    
    model: str
    temperature: float = 0.1
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[str] = None  # "auto", "none", or specific function name


class AIService(ABC, LoggerMixin):
    """
    Abstract base class for AI service implementations.
    
    Provides a consistent interface for interacting with different AI providers
    like Anthropic Claude, OpenAI GPT, etc.
    """
    
    def __init__(self, api_key: str, default_model: str) -> None:
        """
        Initialize AI service.
        
        Args:
            api_key: API key for the AI provider
            default_model: Default model to use for requests
        """
        self.api_key = api_key
        self.default_model = default_model
        self._client = None
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of the AI provider."""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """Get list of supported models."""
        pass
    
    @abstractmethod
    async def _initialize_client(self) -> None:
        """Initialize the AI provider client."""
        pass
    
    @abstractmethod
    async def _make_request(
        self,
        messages: List[AIMessage],
        config: AIModelConfig
    ) -> AIResponse:
        """Make a request to the AI provider."""
        pass
    
    async def ensure_client(self) -> None:
        """Ensure the client is initialized."""
        if self._client is None:
            await self._initialize_client()
    
    async def generate_response(
        self,
        messages: List[AIMessage],
        config: Optional[AIModelConfig] = None
    ) -> AIResponse:
        """
        Generate a response from the AI model.
        
        Args:
            messages: List of messages in the conversation
            config: Model configuration (uses defaults if not provided)
            
        Returns:
            AIResponse: The AI model's response
            
        Raises:
            AIModelError: If the request fails
        """
        await self.ensure_client()
        
        if config is None:
            config = AIModelConfig(model=self.default_model)
        
        start_time = time.time()
        
        try:
            self.logger.info(
                "Making AI request",
                provider=self.provider_name,
                model=config.model,
                message_count=len(messages)
            )
            
            response = await self._make_request(messages, config)
            
            self.logger.info(
                "AI request completed",
                provider=self.provider_name,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                processing_time_ms=response.processing_time_ms
            )
            
            return response
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            self.logger.error(
                "AI request failed",
                provider=self.provider_name,
                model=config.model,
                error=str(e),
                processing_time_ms=processing_time,
                exc_info=True
            )
            
            raise AIModelError(
                f"AI request failed: {str(e)}",
                model_name=config.model,
                provider=self.provider_name,
                context={
                    "message_count": len(messages),
                    "processing_time_ms": processing_time
                }
            )
    
    async def generate_streaming_response(
        self,
        messages: List[AIMessage],
        config: Optional[AIModelConfig] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the AI model.
        
        Args:
            messages: List of messages in the conversation
            config: Model configuration (uses defaults if not provided)
            
        Yields:
            str: Chunks of the AI model's response
            
        Raises:
            AIModelError: If the request fails
        """
        # Default implementation - subclasses can override for true streaming
        response = await self.generate_response(messages, config)
        yield response.content
    
    async def generate_code(
        self,
        specification: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """
        Generate code from a natural language specification.
        
        Args:
            specification: Natural language description of the code to generate
            language: Programming language for the generated code
            context: Additional context for code generation
            
        Returns:
            AIResponse: Response containing the generated code
        """
        system_prompt = f"""You are an expert {language} developer specializing in integration code generation.
Generate clean, production-ready code that follows best practices and includes proper error handling.
Always include type hints, docstrings, and comprehensive error handling.
Focus on creating maintainable, testable code."""
        
        user_message = f"""Generate {language} code for the following specification:

{specification}"""
        
        if context:
            user_message += f"\n\nAdditional context:\n{context}"
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=user_message)
        ]
        
        config = AIModelConfig(
            model=self.default_model,
            temperature=0.1,  # Low temperature for more deterministic code generation
            max_tokens=4096
        )
        
        return await self.generate_response(messages, config)
    
    async def analyze_integration_requirements(
        self,
        natural_language_spec: str,
        source_system: Optional[Dict[str, Any]] = None,
        target_system: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """
        Analyze natural language integration requirements.
        
        Args:
            natural_language_spec: Natural language description of the integration
            source_system: Information about the source system
            target_system: Information about the target system
            
        Returns:
            AIResponse: Analysis of the integration requirements
        """
        system_prompt = """You are an expert integration architect. Analyze the given integration requirements and provide:

1. Integration type (sync, async, webhook, batch, etc.)
2. Data flow direction and patterns
3. Required transformations
4. Error handling requirements
5. Security considerations
6. Performance requirements
7. Recommended implementation approach

Provide your analysis in structured JSON format."""
        
        user_message = f"Analyze this integration requirement:\n\n{natural_language_spec}"
        
        if source_system:
            user_message += f"\n\nSource system: {source_system}"
        
        if target_system:
            user_message += f"\n\nTarget system: {target_system}"
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=user_message)
        ]
        
        config = AIModelConfig(
            model=self.default_model,
            temperature=0.2,
            max_tokens=2048
        )
        
        return await self.generate_response(messages, config)
    
    def validate_model(self, model: str) -> bool:
        """
        Validate if a model is supported by this provider.
        
        Args:
            model: Model name to validate
            
        Returns:
            bool: True if model is supported
        """
        return model in self.supported_models
    
    async def health_check(self) -> bool:
        """
        Check if the AI service is healthy and accessible.
        
        Returns:
            bool: True if service is healthy
        """
        try:
            await self.ensure_client()
            
            # Simple test request
            messages = [AIMessage(role="user", content="Hello")]
            config = AIModelConfig(model=self.default_model, max_tokens=10)
            
            await self.generate_response(messages, config)
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed for {self.provider_name}", error=str(e))
            return False
