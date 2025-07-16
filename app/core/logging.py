"""
Structured logging configuration for the agentic integration platform.

This module provides centralized logging setup with support for structured JSON logging,
correlation IDs, and integration with OpenTelemetry for distributed tracing.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

import structlog
from opentelemetry import trace

from app.core.config import settings

# Context variables for request correlation
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def add_correlation_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to log events."""
    if correlation_id.get():
        event_dict["correlation_id"] = correlation_id.get()
    if user_id.get():
        event_dict["user_id"] = user_id.get()
    if request_id.get():
        event_dict["request_id"] = request_id.get()
    return event_dict


def add_trace_info(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add OpenTelemetry trace information to log events."""
    span = trace.get_current_span()
    if span and span.is_recording():
        span_context = span.get_span_context()
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        add_correlation_id,
        add_trace_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def set_correlation_id(cid: Optional[str] = None) -> str:
    """Set correlation ID for the current context."""
    if cid is None:
        cid = str(uuid.uuid4())
    correlation_id.set(cid)
    return cid


def set_user_id(uid: str) -> None:
    """Set user ID for the current context."""
    user_id.set(uid)


def set_request_id(rid: Optional[str] = None) -> str:
    """Set request ID for the current context."""
    if rid is None:
        rid = str(uuid.uuid4())
    request_id.set(rid)
    return rid


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id.get()


def get_user_id() -> Optional[str]:
    """Get the current user ID."""
    return user_id.get()


def get_request_id() -> Optional[str]:
    """Get the current request ID."""
    return request_id.get()


class LoggerMixin:
    """Mixin class to add structured logging to any class."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get a logger instance bound to this class."""
        return get_logger(self.__class__.__name__)


# Initialize logging configuration
configure_logging()
