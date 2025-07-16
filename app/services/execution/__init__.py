"""
Integration Execution Services

This package provides the execution capabilities for the agentic integration platform,
allowing the MCP agent to not just plan but also execute integrations in real-time.
"""

from .integration_executor import IntegrationExecutor, ExecutionStep, create_integration_executor

__all__ = [
    "IntegrationExecutor",
    "ExecutionStep", 
    "create_integration_executor"
]
