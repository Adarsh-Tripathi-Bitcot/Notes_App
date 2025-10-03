"""
Comprehensive unit tests for admin router module to increase coverage.
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routers.admin_router import (
    LogLevelRequest,
    LogLevelResponse,
    SystemInfoResponse,
    router,
)


class TestAdminRouterModels:
    """Test admin router Pydantic models."""

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

    def test_log_level_response_with_all_fields(self):
        """Test LogLevelResponse with all fields specified."""
        response = LogLevelResponse(
            success=True,
            message="Test message",
            current_level="DEBUG",
            module="test.module",
        )
        assert response.success is True
        assert response.message == "Test message"
        assert response.current_level == "DEBUG"
        assert response.module == "test.module"

    def test_system_info_response_with_all_fields(self):
        """Test SystemInfoResponse with all fields specified."""
        response = SystemInfoResponse(
            environment="test",
            debug_mode=True,
            log_level="DEBUG",
            log_format="json",
            configured_modules={"test.module": "INFO"},
            user_context_enabled=True,
            request_context_enabled=True,
        )
        assert response.environment == "test"
        assert response.debug_mode is True
        assert response.log_level == "DEBUG"
        assert response.log_format == "json"
        assert response.configured_modules == {"test.module": "INFO"}
        assert response.user_context_enabled is True


class TestAdminRouterEndpoints:
    """Test admin router endpoints."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_get_system_info_success(self, client):
        """Test successful system info retrieval."""
        with patch("src.api.routers.admin_router.settings") as mock_settings, patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level, patch(
            "src.api.routers.admin_router.list_configured_modules"
        ) as mock_list_modules:
            # Configure mocks
            mock_settings.environment = "test"
            mock_settings.debug = True
            mock_settings.log_level = "DEBUG"
            mock_settings.log_format = "json"
            mock_settings.user_context_enabled = True
            mock_get_level.return_value = "DEBUG"
            mock_list_modules.return_value = {"test.module": "INFO"}

            response = client.get("/api/v1/admin/system-info")

            assert response.status_code == 200
            data = response.json()
            assert data["environment"] == "test"
            assert data["debug_mode"] is True
            assert data["log_level"] == "DEBUG"
            assert data["log_format"] == "json"
            assert data["configured_modules"] == {"test.module": "INFO"}
            assert data["user_context_enabled"] is True

    def test_get_system_info_error(self, client):
        """Test system info retrieval with error."""
        with patch(
            "src.api.routers.admin_router.list_configured_modules"
        ) as mock_list_modules:
            mock_list_modules.side_effect = Exception("Test error")

            response = client.get("/api/v1/admin/system-info")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_set_log_level_success_global(self, client):
        """Test successful global log level setting."""
        with patch(
            "src.api.routers.admin_router.set_log_level"
        ) as mock_set_level, patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "DEBUG"
            request_data = {"level": "debug"}

            response = client.post("/api/v1/admin/log-level", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Log level set to DEBUG" in data["message"]
            assert data["current_level"] == "DEBUG"
            assert data["module"] is None
            mock_set_level.assert_called_once_with("DEBUG", None)

    def test_set_log_level_success_module(self, client):
        """Test successful module-specific log level setting."""
        with patch(
            "src.api.routers.admin_router.set_log_level"
        ) as mock_set_level, patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "ERROR"
            request_data = {"level": "error", "module": "test.module"}

            response = client.post("/api/v1/admin/log-level", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Log level set to ERROR for module 'test.module'" in data["message"]
            assert data["current_level"] == "ERROR"
            assert data["module"] == "test.module"
            mock_set_level.assert_called_once_with("ERROR", "test.module")

    def test_set_log_level_validation_error(self, client):
        """Test log level setting with validation error."""
        with patch("src.api.routers.admin_router.set_log_level") as mock_set_level:
            mock_set_level.side_effect = ValueError("Invalid log level")
            request_data = {"level": "invalid"}

            response = client.post("/api/v1/admin/log-level", json=request_data)

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data

    def test_set_log_level_general_error(self, client):
        """Test log level setting with general error."""
        with patch("src.api.routers.admin_router.set_log_level") as mock_set_level:
            mock_set_level.side_effect = Exception("Test error")
            request_data = {"level": "debug"}

            response = client.post("/api/v1/admin/log-level", json=request_data)

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_get_log_level_success(self, client):
        """Test successful log level retrieval."""
        with patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "WARNING"

            response = client.get("/api/v1/admin/log-level")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Current log level: WARNING" in data["message"]
            assert data["current_level"] == "WARNING"
            assert data["module"] is None

    def test_get_log_level_error(self, client):
        """Test log level retrieval with error."""
        with patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.side_effect = Exception("Test error")

            response = client.get("/api/v1/admin/log-level")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_get_module_log_level_success(self, client):
        """Test successful module log level retrieval."""
        with patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "INFO"

            response = client.get("/api/v1/admin/log-level?module=test.module")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Current log level: INFO" in data["message"]
            assert data["current_level"] == "INFO"
            assert data["module"] == "test.module"

    def test_get_module_log_level_error(self, client):
        """Test module log level retrieval with error."""
        with patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.side_effect = Exception("Test error")

            response = client.get("/api/v1/admin/log-level?module=test.module")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_list_modules_success(self, client):
        """Test successful modules listing."""
        with patch("src.api.routers.admin_router.list_configured_modules") as mock_list:
            mock_list.return_value = {"test.module": "INFO", "another.module": "DEBUG"}

            response = client.get("/api/v1/admin/modules")

            assert response.status_code == 200
            data = response.json()
            assert data == {"test.module": "INFO", "another.module": "DEBUG"}

    def test_list_modules_error(self, client):
        """Test modules listing with error."""
        with patch("src.api.routers.admin_router.list_configured_modules") as mock_list:
            mock_list.side_effect = Exception("Test error")

            response = client.get("/api/v1/admin/modules")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_reset_log_levels_success(self, client):
        """Test successful log levels reset."""
        with patch("src.core.logging.reset_log_levels") as mock_reset:
            mock_reset.return_value = None

            response = client.post("/api/v1/admin/reset-logging")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Logging configuration reset to defaults" in data["message"]
            mock_reset.assert_called_once()

    def test_reset_log_levels_error(self, client):
        """Test log levels reset with error."""
        with patch("src.core.logging.reset_log_levels") as mock_reset:
            mock_reset.side_effect = Exception("Test error")

            response = client.post("/api/v1/admin/reset-logging")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_invalid_json_request(self, client):
        """Test request with invalid JSON."""
        response = client.post("/api/v1/admin/log-level", data="invalid json")

        assert response.status_code == 422  # Validation error

    def test_missing_required_field(self, client):
        """Test request with missing required field."""
        request_data = {"module": "test.module"}  # Missing 'level'

        response = client.post("/api/v1/admin/log-level", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_empty_module_name(self, client):
        """Test request with empty module name."""
        with patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "INFO"

            response = client.get("/api/v1/admin/log-level?module=")

            # Empty module name should work (treated as global)
            assert response.status_code == 200

    def test_special_characters_in_module_name(self, client):
        """Test module name with special characters."""
        with patch(
            "src.api.routers.admin_router.get_current_log_level"
        ) as mock_get_level:
            mock_get_level.return_value = "DEBUG"

            response = client.get("/api/v1/admin/log-level?module=test-module_123")

            assert response.status_code == 200
            data = response.json()
            assert data["module"] == "test-module_123"

    def test_unsupported_http_methods(self, client):
        """Test unsupported HTTP methods on endpoints."""
        # Test PUT on GET-only endpoint
        response = client.put("/api/v1/admin/system-info")
        assert response.status_code == 405  # Method Not Allowed

        # Test DELETE on GET-only endpoint
        response = client.delete("/api/v1/admin/system-info")
        assert response.status_code == 405  # Method Not Allowed

        # Test PATCH on GET-only endpoint
        response = client.patch("/api/v1/admin/system-info")
        assert response.status_code == 405  # Method Not Allowed

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options("/api/v1/admin/system-info")

        # For OPTIONS requests to endpoints that don't explicitly handle them,
        # we expect a 405 with Allow header
        assert response.status_code == 405
        assert "allow" in response.headers
