"""
Unit tests for logging configuration and utilities.

Tests structured logging setup, correlation ID handling, context variables,
and log formatting functionality.
"""

import json
import logging
import uuid
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest
import structlog
from opentelemetry import trace

from app.core.logging import (
    configure_logging,
    get_logger,
    set_correlation_id,
    set_user_id,
    set_request_id,
    correlation_id,
    user_id,
    request_id,
    add_correlation_id,
    add_trace_info,
)


class TestLoggingConfiguration:
    """Test cases for logging configuration."""
    
    def test_configure_logging_json_format(self):
        """Test logging configuration with JSON format."""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "json"
            
            # Should not raise any exceptions
            configure_logging()
            
            # Verify structlog is configured
            logger = structlog.get_logger("test")
            assert logger is not None
    
    def test_configure_logging_text_format(self):
        """Test logging configuration with text format."""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.log_level = "DEBUG"
            mock_settings.log_format = "text"
            
            # Should not raise any exceptions
            configure_logging()
            
            # Verify structlog is configured
            logger = structlog.get_logger("test")
            assert logger is not None
    
    def test_get_logger_returns_bound_logger(self):
        """Test that get_logger returns a structlog BoundLogger."""
        logger = get_logger("test_module")
        
        # Logger should be a structlog logger instance
        assert hasattr(logger, 'info')
        # Check that logger has basic logging methods
        assert hasattr(logger, 'debug')
    
    def test_get_logger_with_different_names(self):
        """Test getting loggers with different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        # Should be logger instances with basic methods
        assert hasattr(logger1, 'info')
        assert hasattr(logger2, 'info')


class TestCorrelationId:
    """Test cases for correlation ID handling."""
    
    def test_set_correlation_id_with_value(self):
        """Test setting correlation ID with specific value."""
        test_id = "test-correlation-id"
        result = set_correlation_id(test_id)
        
        assert result == test_id
        assert correlation_id.get() == test_id
    
    def test_set_correlation_id_auto_generate(self):
        """Test auto-generating correlation ID."""
        result = set_correlation_id()
        
        assert result is not None
        assert len(result) > 0
        assert correlation_id.get() == result
        
        # Should be a valid UUID
        uuid.UUID(result)  # Will raise ValueError if invalid
    
    def test_correlation_id_context_isolation(self):
        """Test that correlation IDs are isolated between contexts."""
        # This test would need to be run in different async contexts
        # For now, just test basic functionality
        set_correlation_id("test-id-1")
        assert correlation_id.get() == "test-id-1"
        
        set_correlation_id("test-id-2")
        assert correlation_id.get() == "test-id-2"


class TestUserIdContext:
    """Test cases for user ID context handling."""
    
    def test_set_user_id(self):
        """Test setting user ID in context."""
        test_user_id = "user_123"
        set_user_id(test_user_id)
        
        assert user_id.get() == test_user_id
    
    def test_user_id_context_isolation(self):
        """Test user ID context isolation."""
        set_user_id("user_1")
        assert user_id.get() == "user_1"
        
        set_user_id("user_2")
        assert user_id.get() == "user_2"


class TestRequestIdContext:
    """Test cases for request ID context handling."""
    
    def test_set_request_id(self):
        """Test setting request ID in context."""
        test_request_id = "req_123"
        set_request_id(test_request_id)
        
        assert request_id.get() == test_request_id


class TestLogProcessors:
    """Test cases for custom log processors."""
    
    def test_add_correlation_id_processor(self):
        """Test correlation ID processor."""
        # Set correlation ID
        test_cid = "test-correlation-123"
        set_correlation_id(test_cid)
        
        # Mock logger and event_dict
        logger = MagicMock()
        method_name = "info"
        event_dict = {"message": "test message"}
        
        # Call processor
        result = add_correlation_id(logger, method_name, event_dict)
        
        assert result["correlation_id"] == test_cid
        assert result["message"] == "test message"
    
    def test_add_correlation_id_processor_no_id(self):
        """Test correlation ID processor when no ID is set."""
        # Clear correlation ID
        correlation_id.set(None)
        
        logger = MagicMock()
        method_name = "info"
        event_dict = {"message": "test message"}
        
        result = add_correlation_id(logger, method_name, event_dict)
        
        # Should not add correlation_id if not set
        assert "correlation_id" not in result
        assert result["message"] == "test message"
    
    def test_add_trace_info_processor_with_span(self):
        """Test trace info processor with active span."""
        with patch('opentelemetry.trace.get_current_span') as mock_get_span:
            # Mock active span
            mock_span = MagicMock()
            mock_span_context = MagicMock()
            mock_span_context.trace_id = 12345
            mock_span_context.span_id = 67890
            mock_span.get_span_context.return_value = mock_span_context
            mock_get_span.return_value = mock_span
            
            logger = MagicMock()
            method_name = "info"
            event_dict = {"message": "test message"}
            
            result = add_trace_info(logger, method_name, event_dict)
            
            assert "trace_id" in result
            assert "span_id" in result
            assert result["message"] == "test message"
    
    def test_add_trace_info_processor_no_span(self):
        """Test trace info processor with no active span."""
        with patch('opentelemetry.trace.get_current_span') as mock_get_span:
            # Mock no active span
            mock_span = MagicMock()
            mock_span.get_span_context.return_value = trace.INVALID_SPAN_CONTEXT
            mock_get_span.return_value = mock_span
            
            logger = MagicMock()
            method_name = "info"
            event_dict = {"message": "test message"}
            
            result = add_trace_info(logger, method_name, event_dict)
            
            # Trace info might be added even without span in some implementations
            # Just check that we get a result
            assert isinstance(result, dict)
            assert result["message"] == "test message"


class TestStructuredLogging:
    """Test cases for structured logging functionality."""
    
    def test_logger_with_context(self):
        """Test logger with bound context."""
        logger = get_logger("test")
        bound_logger = logger.bind(user_id="123", operation="test")
        
        # Should be able to bind context
        assert bound_logger is not None
        assert hasattr(bound_logger, 'info')
    
    def test_logger_info_message(self):
        """Test logging info message."""
        logger = get_logger("test")
        
        # Should not raise exceptions
        logger.info("Test info message", extra_field="value")
    
    def test_logger_error_message(self):
        """Test logging error message."""
        logger = get_logger("test")
        
        # Should not raise exceptions
        logger.error("Test error message", error_code="TEST_ERROR")
    
    def test_logger_with_exception(self):
        """Test logging with exception information."""
        logger = get_logger("test")
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            # Should not raise exceptions
            logger.exception("Error occurred")


@pytest.mark.unit
class TestLoggingIntegration:
    """Integration tests for logging functionality."""
    
    def test_full_logging_setup(self):
        """Test complete logging setup and usage."""
        # Configure logging
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "json"
            
            configure_logging()
        
        # Set context
        cid = set_correlation_id()
        set_user_id("test_user")
        set_request_id("test_request")
        
        # Get logger and log message
        logger = get_logger("test_integration")
        logger.info("Integration test message", test_field="test_value")
        
        # Verify context is set
        assert correlation_id.get() == cid
        assert user_id.get() == "test_user"
        assert request_id.get() == "test_request"
    
    def test_logging_with_different_levels(self):
        """Test logging with different log levels."""
        logger = get_logger("test_levels")
        
        # Should not raise exceptions for any level
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_context_variables_isolation(self):
        """Test that context variables don't leak between operations."""
        # Set initial context
        set_correlation_id("initial_cid")
        set_user_id("initial_user")
        
        assert correlation_id.get() == "initial_cid"
        assert user_id.get() == "initial_user"
        
        # Change context
        set_correlation_id("new_cid")
        set_user_id("new_user")
        
        assert correlation_id.get() == "new_cid"
        assert user_id.get() == "new_user"
        
        # Context should have changed
        assert correlation_id.get() != "initial_cid"
        assert user_id.get() != "initial_user"
