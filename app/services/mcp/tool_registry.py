"""
Tool registry for Model Context Protocol implementation.

This module provides a registry for AI tools/functions that can be called
during conversations to perform actions and retrieve information.
"""

import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from functools import wraps

from app.core.logging import LoggerMixin
from app.core.exceptions import ValidationError


@dataclass
class ToolDefinition:
    """Represents a tool/function definition."""
    
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    is_async: bool = False
    category: str = "general"
    
    def to_function_definition(self) -> Dict[str, Any]:
        """Convert to OpenAI function definition format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class ToolRegistry(LoggerMixin):
    """
    Registry for AI tools and functions.
    
    Manages tool registration, validation, and execution
    for use in AI conversations.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, ToolDefinition] = {}
        self._categories: Dict[str, List[str]] = {}
        
        # Register default tools
        self._register_default_tools()
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        category: str = "general"
    ) -> Callable:
        """
        Decorator to register a tool function.
        
        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for parameters
            category: Tool category
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable) -> Callable:
            is_async = inspect.iscoroutinefunction(func)
            
            tool_def = ToolDefinition(
                name=name,
                description=description,
                function=func,
                parameters=parameters,
                is_async=is_async,
                category=category
            )
            
            self._tools[name] = tool_def
            
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(name)
            
            self.logger.info(f"Registered tool: {name} (category: {category})")
            
            return func
        
        return decorator
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            ToolDefinition: Tool definition or None
        """
        return self._tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """
        List available tools.
        
        Args:
            category: Optional category filter
            
        Returns:
            List[ToolDefinition]: Available tools
        """
        if category:
            tool_names = self._categories.get(category, [])
            return [self._tools[name] for name in tool_names]
        
        return list(self._tools.values())
    
    def get_function_definitions(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get function definitions for AI models.
        
        Args:
            category: Optional category filter
            
        Returns:
            List[Dict[str, Any]]: Function definitions
        """
        tools = self.list_tools(category)
        return [tool.to_function_definition() for tool in tools]
    
    async def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool with given arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Any: Tool execution result
            
        Raises:
            ValidationError: If tool not found or execution fails
        """
        tool = self.get_tool(name)
        
        if not tool:
            raise ValidationError(f"Tool not found: {name}")
        
        try:
            self.logger.debug(f"Executing tool: {name}", arguments=arguments)
            
            if tool.is_async:
                result = await tool.function(**arguments)
            else:
                result = tool.function(**arguments)
            
            self.logger.debug(f"Tool execution completed: {name}")
            return result
            
        except Exception as e:
            self.logger.error(
                f"Tool execution failed: {name}",
                error=str(e),
                arguments=arguments,
                exc_info=True
            )
            raise ValidationError(
                f"Tool execution failed: {str(e)}",
                context={"tool": name, "arguments": arguments}
            )
    
    def _register_default_tools(self) -> None:
        """Register default system tools."""
        
        @self.register_tool(
            name="get_current_time",
            description="Get the current date and time",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            category="system"
        )
        def get_current_time() -> str:
            """Get current time."""
            from datetime import datetime
            return datetime.utcnow().isoformat()
        
        @self.register_tool(
            name="search_knowledge_graph",
            description="Search the knowledge graph for entities and relationships",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "entity_type": {
                        "type": "string",
                        "description": "Filter by entity type",
                        "enum": ["business_object", "api_endpoint", "data_field", "system", "process", "rule", "pattern", "transformation"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
            category="knowledge"
        )
        async def search_knowledge_graph(
            query: str,
            entity_type: Optional[str] = None,
            limit: int = 10
        ) -> List[Dict[str, Any]]:
            """Search knowledge graph."""
            # TODO: Implement actual knowledge graph search
            return [
                {
                    "id": "example-entity",
                    "name": f"Example entity for: {query}",
                    "type": entity_type or "business_object",
                    "description": f"Mock entity matching query: {query}"
                }
            ]
        
        @self.register_tool(
            name="get_integration_patterns",
            description="Get integration patterns matching criteria",
            parameters={
                "type": "object",
                "properties": {
                    "source_system_type": {
                        "type": "string",
                        "description": "Source system type"
                    },
                    "target_system_type": {
                        "type": "string",
                        "description": "Target system type"
                    },
                    "pattern_type": {
                        "type": "string",
                        "description": "Pattern type",
                        "enum": ["sync", "async", "webhook", "batch", "realtime", "api_proxy", "etl", "event_driven"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of patterns",
                        "default": 5
                    }
                },
                "required": []
            },
            category="integration"
        )
        async def get_integration_patterns(
            source_system_type: Optional[str] = None,
            target_system_type: Optional[str] = None,
            pattern_type: Optional[str] = None,
            limit: int = 5
        ) -> List[Dict[str, Any]]:
            """Get integration patterns."""
            # TODO: Implement actual pattern search
            return [
                {
                    "id": "example-pattern",
                    "name": f"Pattern for {source_system_type} to {target_system_type}",
                    "type": pattern_type or "sync",
                    "description": "Mock integration pattern",
                    "success_rate": 95.0,
                    "usage_count": 42
                }
            ]
        
        @self.register_tool(
            name="validate_integration_code",
            description="Validate generated integration code",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to validate"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                        "default": "python"
                    }
                },
                "required": ["code"]
            },
            category="validation"
        )
        async def validate_integration_code(
            code: str,
            language: str = "python"
        ) -> Dict[str, Any]:
            """Validate integration code."""
            # TODO: Implement actual code validation
            return {
                "valid": True,
                "score": 8.5,
                "issues": [],
                "suggestions": [
                    "Consider adding more error handling",
                    "Add type hints for better maintainability"
                ]
            }
        
        @self.register_tool(
            name="test_api_endpoint",
            description="Test connectivity to an API endpoint",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "API endpoint URL"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds",
                        "default": 30
                    }
                },
                "required": ["url"]
            },
            category="testing"
        )
        async def test_api_endpoint(
            url: str,
            method: str = "GET",
            headers: Optional[Dict[str, str]] = None,
            timeout: int = 30
        ) -> Dict[str, Any]:
            """Test API endpoint connectivity."""
            import httpx
            
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers or {}
                    )
                    
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "headers": dict(response.headers),
                        "accessible": response.status_code < 400
                    }
            
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "accessible": False
                }
        
        @self.register_tool(
            name="generate_code_documentation",
            description="Generate documentation for code",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to document"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                        "default": "python"
                    },
                    "format": {
                        "type": "string",
                        "description": "Documentation format",
                        "enum": ["markdown", "rst", "docstring"],
                        "default": "markdown"
                    }
                },
                "required": ["code"]
            },
            category="documentation"
        )
        async def generate_code_documentation(
            code: str,
            language: str = "python",
            format: str = "markdown"
        ) -> str:
            """Generate code documentation."""
            # TODO: Implement actual documentation generation
            return f"""# Code Documentation

## Overview
This {language} code provides integration functionality.

## Functions
- Main integration function
- Error handling utilities
- Data transformation helpers

## Usage
```{language}
{code[:200]}...
```

## Notes
Generated documentation for integration code.
"""
    
    def get_categories(self) -> List[str]:
        """
        Get available tool categories.
        
        Returns:
            List[str]: Available categories
        """
        return list(self._categories.keys())
    
    def get_tool_count(self) -> int:
        """
        Get total number of registered tools.
        
        Returns:
            int: Number of tools
        """
        return len(self._tools)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get tool registry statistics.
        
        Returns:
            Dict[str, Any]: Registry statistics
        """
        return {
            "total_tools": len(self._tools),
            "categories": {
                category: len(tools)
                for category, tools in self._categories.items()
            },
            "async_tools": sum(
                1 for tool in self._tools.values() if tool.is_async
            ),
            "sync_tools": sum(
                1 for tool in self._tools.values() if not tool.is_async
            )
        }


# Global tool registry instance
tool_registry = ToolRegistry()
