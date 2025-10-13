"""
Unit tests for middleware module.

This module tests the correlation middleware functionality
including request/response logging and user context extraction.
"""

from unittest.mock import Mock, patch

import pytest

from src.core.logging import add_correlation_context
from src.core.middleware import (
    CorrelationMiddleware,
    generate_correlation_id,
    get_logger,
    setup_logging_middleware,
)


class TestMiddlewareFunctions:
    """Test middleware utility functions."""

    def test_generate_correlation_id(self):
        """Test generating correlation ID."""
        corr_id = generate_correlation_id()
        assert corr_id is not None
        assert isinstance(corr_id, str)
        assert len(corr_id) > 0

    def test_generate_correlation_id_unique(self):
        """Test that generated correlation IDs are unique."""
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()
        assert id1 != id2

    def test_add_correlation_context(self):
        """Test adding correlation context."""
        # Test that add_correlation_context works without errors
        add_correlation_context(user_id="user123", correlation_id="corr123")
        # Function should complete without raising exceptions

    def test_add_correlation_context_with_none_values(self):
        """Test adding correlation context with None values."""
        # Test that add_correlation_context handles None values gracefully
        add_correlation_context(user_id=None, correlation_id=None)
        # Function should complete without raising exceptions

    def test_get_logger(self):
        """Test getting logger."""
        logger = get_logger(__name__)
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_get_logger_different_names(self):
        """Test getting loggers with different names."""
        logger1 = get_logger("test.module1")
        logger2 = get_logger("test.module2")

        assert logger1 is not None
        assert logger2 is not None
        # They should be different instances
        assert logger1 is not logger2

    def test_setup_logging_middleware(self):
        """Test setting up logging middleware."""
        mock_app = Mock()

        with patch("src.core.middleware.CorrelationMiddleware"):
            setup_logging_middleware(mock_app)
            # Should create and add 2 middleware components
            assert mock_app.add_middleware.call_count == 2

    def test_setup_logging_middleware_with_existing_app(self):
        """Test setting up logging middleware with existing app."""
        mock_app = Mock()
        mock_app.add_middleware = Mock()

        with patch("src.core.middleware.CorrelationMiddleware"):
            setup_logging_middleware(mock_app)
            # Should add 2 middleware components to app
            assert mock_app.add_middleware.call_count == 2

    def test_correlation_id_format(self):
        """Test correlation ID format."""
        corr_id = generate_correlation_id()
        # Should be a valid UUID format
        assert len(corr_id) == 36  # UUID length
        assert corr_id.count("-") == 4  # UUID format

    def test_add_correlation_context_multiple_calls(self):
        """Test adding correlation context multiple times."""
        # Test that add_correlation_context can be called multiple times
        add_correlation_context(user_id="user1", correlation_id="corr1")
        add_correlation_context(user_id="user2", correlation_id="corr2")
        # Function should complete without raising exceptions

    def test_logger_with_different_levels(self):
        """Test logger with different log levels."""
        logger = get_logger(__name__)

        # Should be able to log at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        # Should not raise any exceptions
        assert True

    def test_logger_thread_safety(self):
        """Test logger thread safety."""
        import threading
        import time

        logger = get_logger(__name__)
        results = []

        def log_worker(worker_id):
            for i in range(10):
                logger.info(f"Worker {worker_id} message {i}")
                results.append(f"worker_{worker_id}_{i}")
                time.sleep(0.001)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all messages were logged
        assert len(results) == 50  # 5 workers * 10 messages each

    def test_correlation_id_consistency(self):
        """Test correlation ID consistency."""
        # Generate multiple IDs and ensure they're all valid
        ids = [generate_correlation_id() for _ in range(10)]

        # All should be valid UUIDs
        for corr_id in ids:
            assert len(corr_id) == 36
            assert corr_id.count("-") == 4

        # All should be unique
        assert len(set(ids)) == 10

    def test_add_correlation_context_error_handling(self):
        """Test add correlation context error handling."""
        # Test that add_correlation_context handles invalid parameters gracefully
        # The function should not raise exceptions for invalid parameter names
        add_correlation_context(invalid_param="test")
        # Function should complete without raising exceptions

    def test_setup_logging_middleware_error_handling(self):
        """Test setup logging middleware error handling."""
        mock_app = Mock()
        mock_app.add_middleware.side_effect = Exception("Middleware error")

        # Should handle errors gracefully - let it raise the exception
        # as the function doesn't have try-catch
        with pytest.raises(Exception, match="Middleware error"):
            setup_logging_middleware(mock_app)


class TestCorrelationMiddleware:
    """Test CorrelationMiddleware class."""

    def test_middleware_initialization(self):
        """Test middleware initialization."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app, exclude_paths=[])

        assert middleware.app == mock_app
        assert middleware.exclude_paths == []

    def test_middleware_initialization_with_exclude_paths(self):
        """Test middleware initialization with exclude paths."""
        mock_app = Mock()
        exclude_paths = ["/health", "/metrics"]
        middleware = CorrelationMiddleware(mock_app, exclude_paths=exclude_paths)

        assert middleware.app == mock_app
        assert middleware.exclude_paths == exclude_paths

    def test_middleware_logger_initialization(self):
        """Test middleware logger initialization."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        assert hasattr(middleware, "logger")
        assert middleware.logger is not None

    def test_middleware_get_client_ip(self):
        """Test client IP extraction."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Test with X-Forwarded-For header
        mock_request = Mock()
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        ip = middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.1"

        # Test with X-Real-IP header
        mock_request.headers = {"X-Real-IP": "192.168.1.2"}
        ip = middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.2"

        # Test with client host
        mock_request.headers = {}
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.3"
        ip = middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.3"

        # Test fallback
        mock_request.client = None
        ip = middleware._get_client_ip(mock_request)
        assert ip == "unknown"

    def test_middleware_extract_user_id(self):
        """Test user ID extraction."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock the _extract_user_context method
        with patch.object(middleware, "_extract_user_context") as mock_extract:
            # Test with Bearer token
            mock_request = Mock()
            mock_request.headers = {"Authorization": "Bearer test-token"}
            mock_extract.return_value = {"user_id": "extracted_user_id"}
            user_id = middleware._extract_user_id(mock_request)
            assert user_id == "extracted_user_id"

            # Test without token
            mock_request.headers = {}
            mock_extract.return_value = {}
            user_id = middleware._extract_user_id(mock_request)
            assert user_id == "anonymous"

    def test_middleware_extract_user_context(self):
        """Test user context extraction."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Test with auth bypass enabled
        with patch("src.core.middleware.settings") as mock_settings, patch(
            "src.core.middleware.AuthBypass.is_bypass_enabled"
        ) as mock_bypass:
            mock_settings.auth_bypass = True
            mock_settings.test_user_id = "test-123"
            mock_settings.test_user_email = "test@example.com"
            mock_settings.test_user_username = "testuser"
            mock_settings.test_user_full_name = "Test User"
            mock_settings.test_user_display_name = "Test"
            mock_bypass.return_value = True

            mock_request = Mock()
            mock_request.headers = {"Authorization": "Bearer test-token"}

            context = middleware._extract_user_context(mock_request)

            assert context["user_id"] == "test-123"
            assert context["user_email"] == "test@example.com"
            assert context["user_username"] == "testuser"
