"""
Unit tests for logging utilities module.
"""

from unittest.mock import Mock, patch

from src.core.logging_utils import (
    APILogger,
    RepositoryLogger,
    ServiceLogger,
    log_cache_operation,
    log_database_session,
    log_note_operation,
    log_user_operation,
    log_validation,
)


class TestServiceLogger:
    """Test ServiceLogger class."""

    def test_service_logger_initialization(self):
        """Test ServiceLogger initialization."""
        logger = ServiceLogger("test_service")
        assert logger.service_name == "test_service"
        assert logger.logger is not None

    def test_log_operation(self):
        """Test logging service operation."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            service_logger = ServiceLogger("test_service")
            service_logger.log_operation("create_user", user_id="123")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "Service operation: create_user" in call_args[0][0]
            assert call_args[1]["service"] == "test_service"
            assert call_args[1]["operation"] == "create_user"
            assert call_args[1]["user_id"] == "123"

    def test_log_success(self):
        """Test logging successful operation."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            service_logger = ServiceLogger("test_service")
            service_logger.log_success("create_user", user_id="123")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "Service operation completed: create_user" in call_args[0][0]
            assert call_args[1]["status"] == "success"

    def test_log_error(self):
        """Test logging error."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            service_logger = ServiceLogger("test_service")
            error = ValueError("Test error")
            service_logger.log_error("create_user", error, user_id="123")

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "Service operation failed: create_user" in call_args[0][0]
            assert call_args[1]["status"] == "error"
            assert call_args[1]["error"] == "Test error"
            assert call_args[1]["error_type"] == "ValueError"


class TestRepositoryLogger:
    """Test RepositoryLogger class."""

    def test_repository_logger_initialization(self):
        """Test RepositoryLogger initialization."""
        logger = RepositoryLogger("test_repository")
        assert logger.repository_name == "test_repository"
        assert logger.logger is not None

    def test_log_query(self):
        """Test logging database query."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            repo_logger = RepositoryLogger("test_repository")
            repo_logger.log_query("SELECT", "users", user_id="123")

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert "Database query: SELECT" in call_args[0][0]
            assert call_args[1]["repository"] == "test_repository"
            assert call_args[1]["table"] == "users"

    def test_log_success(self):
        """Test logging successful repository operation."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            repo_logger = RepositoryLogger("test_repository")
            repo_logger.log_success("create_user", user_id="123")

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert "Repository operation completed: create_user" in call_args[0][0]
            assert call_args[1]["status"] == "success"

    def test_log_error(self):
        """Test logging repository error."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            repo_logger = RepositoryLogger("test_repository")
            error = ValueError("Test error")
            repo_logger.log_error("create_user", error, user_id="123")

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "Repository operation failed: create_user" in call_args[0][0]
            assert call_args[1]["status"] == "error"
            assert call_args[1]["error"] == "Test error"
            assert call_args[1]["error_type"] == "ValueError"


class TestAPILogger:
    """Test APILogger class."""

    def test_api_logger_initialization(self):
        """Test APILogger initialization."""
        logger = APILogger("test_router")
        assert logger.router_name == "test_router"
        assert logger.logger is not None

    def test_log_request(self):
        """Test logging API request."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            api_logger = APILogger("test_router")
            api_logger.log_request("GET", "/users", user_id="123")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "API request: GET /users" in call_args[0][0]
            assert call_args[1]["router"] == "test_router"
            assert call_args[1]["method"] == "GET"
            assert call_args[1]["path"] == "/users"

    def test_log_response(self):
        """Test logging API response."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            api_logger = APILogger("test_router")
            api_logger.log_response("GET", "/users", 200, user_id="123")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "API response: GET /users - 200" in call_args[0][0]
            assert call_args[1]["status_code"] == 200

    def test_log_error(self):
        """Test logging API error."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            api_logger = APILogger("test_router")
            error = ValueError("Test error")
            api_logger.log_error("GET", "/users", error, user_id="123")

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "API error: GET /users" in call_args[0][0]
            assert call_args[1]["error"] == "Test error"
            assert call_args[1]["error_type"] == "ValueError"


class TestUtilityFunctions:
    """Test utility logging functions."""

    def test_log_user_operation_with_user_id(self):
        """Test logging user operation with provided user ID."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_user_operation("create_user", user_id_val="123", extra="data")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "User operation: create_user" in call_args[0][0]
            assert call_args[1]["user_id"] == "123"
            assert call_args[1]["extra"] == "data"

    def test_log_user_operation_without_user_id(self):
        """Test logging user operation without provided user ID."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger, patch(
            "src.core.logging_utils.get_user_id"
        ) as mock_get_user_id:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            mock_get_user_id.return_value = "current_user"

            log_user_operation("create_user", extra="data")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "User operation: create_user" in call_args[0][0]
            assert call_args[1]["user_id"] == "current_user"

    def test_log_note_operation(self):
        """Test logging note operation."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger, patch(
            "src.core.logging_utils.get_user_id"
        ) as mock_get_user_id:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            mock_get_user_id.return_value = "current_user"

            log_note_operation("create_note", note_id="note123", extra="data")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "Note operation: create_note" in call_args[0][0]
            assert call_args[1]["note_id"] == "note123"
            assert call_args[1]["user_id"] == "current_user"

    def test_log_validation(self):
        """Test logging validation."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_validation("email_validator", "email", "test@example.com", extra="data")

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert "Validation: email_validator" in call_args[0][0]
            assert call_args[1]["validator"] == "email_validator"
            assert call_args[1]["field"] == "email"
            assert call_args[1]["value"] == "test@example.com"

    def test_log_validation_long_value(self):
        """Test logging validation with long value (truncated)."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            long_value = "x" * 150
            log_validation("email_validator", "email", long_value)

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert call_args[1]["value"] == "x" * 100  # Truncated to 100 chars

    def test_log_validation_none_value(self):
        """Test logging validation with None value."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_validation("email_validator", "email", None)

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert call_args[1]["value"] is None

    def test_log_cache_operation(self):
        """Test logging cache operation."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_cache_operation("get", "user:123", extra="data")

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert "Cache operation: get" in call_args[0][0]
            assert call_args[1]["operation"] == "get"
            assert call_args[1]["key"] == "user:123"

    def test_log_database_session(self):
        """Test logging database session operation."""
        with patch("src.core.logging_utils.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_database_session("begin", extra="data")

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert "Database session: begin" in call_args[0][0]
            assert call_args[1]["operation"] == "begin"
