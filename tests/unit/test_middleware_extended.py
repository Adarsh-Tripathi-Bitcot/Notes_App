"""
Comprehensive unit tests for middleware module to increase coverage.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import Request, Response

from src.core.middleware import CorrelationMiddleware, setup_logging_middleware


class TestCorrelationMiddlewareComprehensive:
    """Comprehensive tests for CorrelationMiddleware to increase coverage."""

    def test_dispatch_successful_request(self):
        """Test successful request processing."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/test"
        mock_request.method = "GET"
        mock_request.query_params = {"param": "value"}
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.client.host = "127.0.0.1"

        # Mock response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}

        # Mock call_next
        async def mock_call_next(request):
            return mock_response

        with patch(
            "src.core.middleware.generate_correlation_id"
        ) as mock_gen_id, patch.object(
            middleware, "_extract_user_context"
        ) as mock_extract, patch.object(
            middleware, "_get_client_ip"
        ) as mock_get_ip:
            mock_gen_id.return_value = "test-correlation-id"
            mock_extract.return_value = {"user_id": "test-user"}
            mock_get_ip.return_value = "127.0.0.1"

            # Run the test
            import asyncio

            result = asyncio.run(middleware.dispatch(mock_request, mock_call_next))

            # Assertions
            assert result == mock_response
            assert result.headers["X-Correlation-ID"] == "test-correlation-id"
            mock_extract.assert_called_once_with(mock_request)

    def test_dispatch_request_with_exception(self):
        """Test request processing with exception."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/test"
        mock_request.method = "GET"
        mock_request.query_params = {}
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.client.host = "127.0.0.1"

        # Mock call_next to raise exception
        async def mock_call_next(request):
            raise ValueError("Test error")

        with patch(
            "src.core.middleware.generate_correlation_id"
        ) as mock_gen_id, patch.object(
            middleware, "_extract_user_context"
        ) as mock_extract, patch.object(
            middleware, "_get_client_ip"
        ) as mock_get_ip:
            mock_gen_id.return_value = "test-correlation-id"
            mock_extract.return_value = {}
            mock_get_ip.return_value = "127.0.0.1"

            # Run the test and expect exception
            import asyncio

            with pytest.raises(ValueError, match="Test error"):
                asyncio.run(middleware.dispatch(mock_request, mock_call_next))

    def test_extract_user_context_with_bearer_token(self):
        """Test user context extraction with Bearer token."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request with Bearer token
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer test-token"}

        with patch("src.core.middleware.settings") as mock_settings, patch(
            "jose.jwt"
        ) as mock_jwt, patch(
            "src.core.database.SessionLocal"
        ) as mock_session_local, patch(
            "src.repositories.user_repository.UserRepository"
        ) as mock_user_repo:
            # Configure mocks
            mock_settings.auth_bypass = False
            mock_settings.jwt_secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"

            mock_jwt.decode.return_value = {"sub": "123"}

            mock_db = Mock()
            mock_session_local.return_value = mock_db

            mock_user = Mock()
            mock_user.id = 123
            mock_user.email = "test@example.com"
            mock_user.username = "testuser"
            mock_user.full_name = "Test User"
            mock_user.display_name = "Test User"

            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo.return_value = mock_repo

            # Run the test
            result = middleware._extract_user_context(mock_request)

            # Assertions
            assert result["user_id"] == "123"
            assert result["user_email"] == "test@example.com"
            assert result["user_username"] == "testuser"
            mock_db.close.assert_called_once()

    def test_extract_user_context_with_auth_bypass(self):
        """Test user context extraction with auth bypass enabled."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer test-token"}

        with patch("src.core.middleware.settings") as mock_settings, patch(
            "src.core.middleware.AuthBypass.is_bypass_enabled"
        ) as mock_bypass:
            # Configure auth bypass
            mock_settings.auth_bypass = True
            mock_settings.test_user_id = "test-user-id"
            mock_settings.test_user_email = "test@example.com"
            mock_settings.test_user_username = "testuser"
            mock_settings.test_user_full_name = "Test User"
            mock_settings.test_user_display_name = "testuser"
            mock_bypass.return_value = True

            # Run the test
            result = middleware._extract_user_context(mock_request)

            # Assertions
            assert result["user_id"] == "test-user-id"
            assert result["user_email"] == "test@example.com"
            assert result["user_username"] == "testuser"
            assert result["user_full_name"] == "Test User"
            assert result["user_display_name"] == "testuser"

    def test_extract_user_context_no_auth_header(self):
        """Test user context extraction without auth header."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request without auth header
        mock_request = Mock(spec=Request)
        mock_request.headers = {}

        # Run the test
        result = middleware._extract_user_context(mock_request)

        # Assertions
        assert result == {}

    def test_extract_user_context_invalid_token(self):
        """Test user context extraction with invalid token."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request with invalid token
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer invalid-token"}

        with patch("src.core.middleware.settings") as mock_settings, patch(
            "jose.jwt"
        ) as mock_jwt:
            # Configure mocks
            mock_settings.auth_bypass = False
            mock_settings.jwt_secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"

            mock_jwt.decode.side_effect = Exception("Invalid token")

            # Run the test
            result = middleware._extract_user_context(mock_request)

            # Assertions
            assert result == {}

    def test_extract_user_context_no_user_id_in_token(self):
        """Test user context extraction with token missing user ID."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer test-token"}

        with patch("src.core.middleware.settings") as mock_settings, patch(
            "jose.jwt"
        ) as mock_jwt:
            # Configure mocks
            mock_settings.auth_bypass = False
            mock_settings.jwt_secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"

            mock_jwt.decode.return_value = {}  # No 'sub' field

            # Run the test
            result = middleware._extract_user_context(mock_request)

            # Assertions
            assert result == {}

    def test_extract_user_context_user_not_found(self):
        """Test user context extraction when user not found in database."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer test-token"}

        with patch("src.core.middleware.settings") as mock_settings, patch(
            "jose.jwt"
        ) as mock_jwt, patch(
            "src.core.database.SessionLocal"
        ) as mock_session_local, patch(
            "src.repositories.user_repository.UserRepository"
        ) as mock_user_repo:
            # Configure mocks
            mock_settings.auth_bypass = False
            mock_settings.jwt_secret_key = "secret"
            mock_settings.jwt_algorithm = "HS256"

            mock_jwt.decode.return_value = {"sub": "123"}

            mock_db = Mock()
            mock_session_local.return_value = mock_db

            mock_repo = Mock()
            mock_repo.get_by_id.return_value = None  # User not found
            mock_user_repo.return_value = mock_repo

            # Run the test
            result = middleware._extract_user_context(mock_request)

            # Assertions
            assert result == {}
            mock_db.close.assert_called_once()

    def test_get_client_ip_x_forwarded_for(self):
        """Test client IP extraction with X-Forwarded-For header."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request with X-Forwarded-For header
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}

        # Run the test
        result = middleware._get_client_ip(mock_request)

        # Assertions
        assert result == "192.168.1.1"  # First IP in the list

    def test_get_client_ip_x_real_ip(self):
        """Test client IP extraction with X-Real-IP header."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request with X-Real-IP header
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Real-IP": "192.168.1.1"}

        # Run the test
        result = middleware._get_client_ip(mock_request)

        # Assertions
        assert result == "192.168.1.1"

    def test_get_client_ip_from_client_host(self):
        """Test client IP extraction from client.host."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request with client.host
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.1"

        # Run the test
        result = middleware._get_client_ip(mock_request)

        # Assertions
        assert result == "192.168.1.1"

    def test_get_client_ip_unknown(self):
        """Test client IP extraction when no IP information available."""
        mock_app = Mock()
        middleware = CorrelationMiddleware(mock_app)

        # Mock request without IP headers or client
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.client = None

        # Run the test
        result = middleware._get_client_ip(mock_request)

        # Assertions
        assert result == "unknown"

    def test_middleware_initialization_with_exclude_paths(self):
        """Test middleware initialization with exclude paths."""
        mock_app = Mock()
        exclude_paths = ["/health", "/metrics"]

        middleware = CorrelationMiddleware(mock_app, exclude_paths=exclude_paths)

        # Assertions
        assert middleware.exclude_paths == exclude_paths
        assert middleware.app == mock_app

    def test_middleware_initialization_without_exclude_paths(self):
        """Test middleware initialization without exclude paths."""
        mock_app = Mock()

        middleware = CorrelationMiddleware(mock_app)

        # Assertions
        assert middleware.exclude_paths == ["/health", "/metrics", "/favicon.ico"]
        assert middleware.app == mock_app


class TestSetupLoggingMiddlewareComprehensive:
    """Comprehensive tests for setup_logging_middleware function."""

    def test_setup_logging_middleware(self):
        """Test setting up logging middleware."""
        mock_app = Mock()

        with patch(
            "src.core.middleware.ProfessionalCorrelationMiddleware"
        ) as mock_middleware_class:
            setup_logging_middleware(mock_app)

            # Assertions
            assert mock_app.add_middleware.call_count == 2
            call_args = mock_app.add_middleware.call_args
            assert call_args[0][0] == mock_middleware_class
            assert call_args[1]["exclude_paths"] == []

    def test_setup_logging_middleware_with_exclude_paths(self):
        """Test setting up logging middleware with exclude paths."""
        mock_app = Mock()
        exclude_paths = ["/health", "/metrics"]

        with patch(
            "src.core.middleware.ProfessionalCorrelationMiddleware"
        ) as mock_middleware_class:
            setup_logging_middleware(mock_app, exclude_paths=exclude_paths)

            # Assertions
            assert mock_app.add_middleware.call_count == 2
            call_args = mock_app.add_middleware.call_args
            assert call_args[0][0] == mock_middleware_class
            assert call_args[1]["exclude_paths"] == exclude_paths
