"""
AI service factory for the agentic integration platform.

This module provides a factory for creating AI service instances
based on configuration and provider selection.
"""

from typing import Dict, Type, Optional

from app.services.ai.base import AIService
from app.services.ai.anthropic_service import AnthropicService
from app.services.ai.openai_service import OpenAIService
from app.core.config import settings
from app.core.exceptions import ConfigurationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIServiceFactory:
    """
    Factory for creating AI service instances.
    
    Manages the creation and configuration of different AI service providers
    based on application settings and runtime requirements.
    """
    
    # Registry of available AI service implementations
    _services: Dict[str, Type[AIService]] = {
        "anthropic": AnthropicService,
        "openai": OpenAIService,
    }
    
    # Cache for service instances
    _instances: Dict[str, AIService] = {}
    
    @classmethod
    def register_service(cls, provider: str, service_class: Type[AIService]) -> None:
        """
        Register a new AI service implementation.
        
        Args:
            provider: Provider name (e.g., "anthropic", "openai")
            service_class: AI service implementation class
        """
        cls._services[provider] = service_class
        logger.info(f"Registered AI service: {provider}")
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of available AI providers.
        
        Returns:
            list[str]: List of provider names
        """
        return list(cls._services.keys())
    
    @classmethod
    def create_service(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> AIService:
        """
        Create an AI service instance.
        
        Args:
            provider: AI provider name (defaults to configured default)
            model: Model name (defaults to configured default)
            api_key: API key (defaults to configured key for provider)
            
        Returns:
            AIService: Configured AI service instance
            
        Raises:
            ConfigurationError: If provider is not supported or configuration is invalid
        """
        # Use defaults from settings if not provided
        if provider is None:
            provider = settings.default_llm_provider
        
        if model is None:
            model = settings.default_model
        
        # Validate provider
        if provider not in cls._services:
            raise ConfigurationError(
                f"Unsupported AI provider: {provider}. Available providers: {list(cls._services.keys())}",
                config_key="default_llm_provider"
            )
        
        # Get API key for provider
        if api_key is None:
            api_key = cls._get_api_key_for_provider(provider)
        
        # Create cache key
        cache_key = f"{provider}:{model}:{hash(api_key)}"
        
        # Return cached instance if available
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Create new service instance
        service_class = cls._services[provider]
        service = service_class(api_key=api_key, default_model=model)
        
        # Validate model is supported
        if not service.validate_model(model):
            raise ConfigurationError(
                f"Model '{model}' is not supported by provider '{provider}'. "
                f"Supported models: {service.supported_models}",
                config_key="default_model"
            )
        
        # Cache the instance
        cls._instances[cache_key] = service
        
        logger.info(
            "Created AI service instance",
            provider=provider,
            model=model,
            cache_key=cache_key
        )
        
        return service
    
    @classmethod
    def get_default_service(cls) -> AIService:
        """
        Get the default AI service instance.
        
        Returns:
            AIService: Default configured AI service
        """
        return cls.create_service()
    
    @classmethod
    def create_anthropic_service(cls, model: Optional[str] = None) -> AnthropicService:
        """
        Create an Anthropic service instance.
        
        Args:
            model: Claude model name
            
        Returns:
            AnthropicService: Anthropic service instance
        """
        service = cls.create_service(provider="anthropic", model=model)
        return service  # type: ignore
    
    @classmethod
    def create_openai_service(cls, model: Optional[str] = None) -> OpenAIService:
        """
        Create an OpenAI service instance.
        
        Args:
            model: GPT model name
            
        Returns:
            OpenAIService: OpenAI service instance
        """
        service = cls.create_service(provider="openai", model=model)
        return service  # type: ignore
    
    @classmethod
    def _get_api_key_for_provider(cls, provider: str) -> str:
        """
        Get API key for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            str: API key for the provider
            
        Raises:
            ConfigurationError: If API key is not configured
        """
        api_key_map = {
            "anthropic": settings.anthropic_api_key,
            "openai": settings.openai_api_key,
        }
        
        api_key = api_key_map.get(provider)
        
        if not api_key:
            raise ConfigurationError(
                f"API key not configured for provider '{provider}'",
                config_key=f"{provider}_api_key"
            )
        
        return api_key
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the service instance cache."""
        cls._instances.clear()
        logger.info("AI service cache cleared")
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, bool]:
        """
        Perform health checks on all configured providers.
        
        Returns:
            Dict[str, bool]: Health status for each provider
        """
        results = {}
        
        for provider in cls._services.keys():
            try:
                service = cls.create_service(provider=provider)
                is_healthy = await service.health_check()
                results[provider] = is_healthy
                
                logger.info(
                    "AI service health check completed",
                    provider=provider,
                    healthy=is_healthy
                )
                
            except Exception as e:
                results[provider] = False
                logger.error(
                    "AI service health check failed",
                    provider=provider,
                    error=str(e)
                )
        
        return results
    
    @classmethod
    def get_service_info(cls, provider: str) -> Dict[str, any]:
        """
        Get information about a specific AI service provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dict[str, any]: Service information
            
        Raises:
            ConfigurationError: If provider is not supported
        """
        if provider not in cls._services:
            raise ConfigurationError(
                f"Unsupported AI provider: {provider}",
                config_key="provider"
            )
        
        service_class = cls._services[provider]
        
        # Create a temporary instance to get info
        try:
            api_key = cls._get_api_key_for_provider(provider)
            temp_service = service_class(api_key=api_key, default_model="dummy")
            
            return {
                "provider": provider,
                "supported_models": temp_service.supported_models,
                "provider_name": temp_service.provider_name,
                "class_name": service_class.__name__,
            }
            
        except Exception as e:
            logger.warning(
                f"Could not get full info for provider {provider}",
                error=str(e)
            )
            
            return {
                "provider": provider,
                "supported_models": [],
                "provider_name": provider,
                "class_name": service_class.__name__,
                "error": str(e)
            }
