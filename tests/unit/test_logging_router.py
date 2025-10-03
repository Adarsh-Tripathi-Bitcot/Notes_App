"""
Unit tests for logging router module.
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routers.logging_router import LogLevelRequest, LogLevelResponse, router


class TestLogLevelRequest:
    """Test LogLevelRequest model."""

    def test_log_level_request_with_level_only(self):
        """Test LogLevelRequest with only level specified."""
        request = LogLevelRequest(level="DEBUG")
        assert request.level == "DEBUG"
        assert request.module is None

    def test_log_level_request_with_level_and_module(self):
        """Test LogLevelRequest with both level and module specified."""
        request = LogLevelRequest(level="INFO", module="test.module")
        assert request.level == "INFO"
        assert request.module == "test.module"


class TestLogLevelResponse:
    """Test LogLevelResponse model."""

    def test_log_level_response_with_message_only(self):
        """Test LogLevelResponse with only message specified."""
        response = LogLevelResponse(message="Test message")
        assert response.message == "Test message"
        assert response.level is None
        assert response.module is None

    def test_log_level_response_with_all_fields(self):
        """Test LogLevelResponse with all fields specified."""
        response = LogLevelResponse(
            message="Test message", level="DEBUG", module="test.module"
        )
        assert response.message == "Test message"
        assert response.level == "DEBUG"
        assert response.module == "test.module"


class TestLoggingRouterEndpoints:
    """Test logging router endpoints."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/logging")
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_get_logging_status_success(self, client):
        """Test successful logging status retrieval."""
        with patch(
            "src.api.routers.logging_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "INFO"

            response = client.get("/api/v1/logging/status")

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Logging status retrieved successfully"
            assert data["level"] == "INFO"
            assert data["module"] == "root"
            mock_get_level.assert_called_once()

    def test_get_logging_status_error(self, client):
        """Test logging status retrieval with error."""
        with patch(
            "src.api.routers.logging_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.side_effect = Exception("Test error")

            response = client.get("/api/v1/logging/status")

            assert response.status_code == 500
            data = response.json()
            assert "Failed to get logging status: Test error" in data["detail"]

    def test_set_logging_level_success_global(self, client):
        """Test successful global log level setting."""
        with patch("src.api.routers.logging_router.set_log_level") as mock_set_level:
            request_data = {"level": "debug"}

            response = client.post("/api/v1/logging/set-level", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Log level set to DEBUG for root"
            assert data["level"] == "DEBUG"
            assert data["module"] is None
            mock_set_level.assert_called_once_with("debug", None)

    def test_set_logging_level_success_module(self, client):
        """Test successful module-specific log level setting."""
        with patch("src.api.routers.logging_router.set_log_level") as mock_set_level:
            request_data = {"level": "error", "module": "test.module"}

            response = client.post("/api/v1/logging/set-level", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Log level set to ERROR for test.module"
            assert data["level"] == "ERROR"
            assert data["module"] == "test.module"
            mock_set_level.assert_called_once_with("error", "test.module")

    def test_set_logging_level_validation_error(self, client):
        """Test log level setting with validation error."""
        with patch("src.api.routers.logging_router.set_log_level") as mock_set_level:
            mock_set_level.side_effect = ValueError("Invalid log level")
            request_data = {"level": "invalid"}

            response = client.post("/api/v1/logging/set-level", json=request_data)

            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "Invalid log level"

    def test_set_logging_level_general_error(self, client):
        """Test log level setting with general error."""
        with patch("src.api.routers.logging_router.set_log_level") as mock_set_level:
            mock_set_level.side_effect = Exception("Test error")
            request_data = {"level": "debug"}

            response = client.post("/api/v1/logging/set-level", json=request_data)

            assert response.status_code == 500
            data = response.json()
            assert "Failed to set log level: Test error" in data["detail"]

    def test_get_module_log_level_success(self, client):
        """Test successful module log level retrieval."""
        with patch(
            "src.api.routers.logging_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "WARNING"

            response = client.get("/api/v1/logging/level/test.module")

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Log level for test.module is WARNING"
            assert data["level"] == "WARNING"
            assert data["module"] == "test.module"
            mock_get_level.assert_called_once_with("test.module")

    def test_get_module_log_level_error(self, client):
        """Test module log level retrieval with error."""
        with patch(
            "src.api.routers.logging_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.side_effect = Exception("Test error")

            response = client.get("/api/v1/logging/level/test.module")

            assert response.status_code == 500
            data = response.json()
            assert "Failed to get log level: Test error" in data["detail"]

    def test_list_modules_success(self, client):
        """Test successful modules listing."""
        with patch(
            "src.api.routers.logging_router.list_configured_modules"
        ) as mock_list:
            mock_list.return_value = {"test.module": "INFO", "another.module": "DEBUG"}

            response = client.get("/api/v1/logging/modules")

            assert response.status_code == 200
            data = response.json()
            assert data == {"test.module": "INFO", "another.module": "DEBUG"}
            mock_list.assert_called_once()

    def test_list_modules_error(self, client):
        """Test modules listing with error."""
        with patch(
            "src.api.routers.logging_router.list_configured_modules"
        ) as mock_list:
            mock_list.side_effect = Exception("Test error")

            response = client.get("/api/v1/logging/modules")

            assert response.status_code == 500
            data = response.json()
            assert "Failed to list modules: Test error" in data["detail"]

    def test_reset_logging_success(self, client):
        """Test successful logging reset."""
        with patch("src.api.routers.logging_router.reset_log_levels") as mock_reset:
            response = client.post("/api/v1/logging/reset")

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "All log levels reset to default configuration"
            assert data["level"] is None
            assert data["module"] is None
            mock_reset.assert_called_once()

    def test_reset_logging_error(self, client):
        """Test logging reset with error."""
        with patch("src.api.routers.logging_router.reset_log_levels") as mock_reset:
            mock_reset.side_effect = Exception("Test error")

            response = client.post("/api/v1/logging/reset")

            assert response.status_code == 500
            data = response.json()
            assert "Failed to reset log levels: Test error" in data["detail"]

    def test_invalid_json_request(self, client):
        """Test request with invalid JSON."""
        response = client.post("/api/v1/logging/set-level", data="invalid json")

        assert response.status_code == 422  # Validation error

    def test_missing_required_field(self, client):
        """Test request with missing required field."""
        request_data = {"module": "test.module"}  # Missing 'level'

        response = client.post("/api/v1/logging/set-level", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_empty_module_name(self, client):
        """Test request with empty module name."""
        with patch(
            "src.api.routers.logging_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "INFO"

            response = client.get("/api/v1/logging/level/")

            # This should result in a 404 since the route expects a module name
            assert response.status_code == 404

    def test_special_characters_in_module_name(self, client):
        """Test module name with special characters."""
        with patch(
            "src.api.routers.logging_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "DEBUG"

            response = client.get("/api/v1/logging/level/test-module_123")

            assert response.status_code == 200
            data = response.json()
            assert data["module"] == "test-module_123"
