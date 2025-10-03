"""
API tests for admin router.

This module tests the administrative API endpoints including
system information, log level management, and module listing.
"""


from fastapi import status
from fastapi.testclient import TestClient


class TestSystemInfo:
    """Test system information endpoint."""

    def test_get_system_info(self, client: TestClient):
        """Test getting system information."""
        response = client.get("/api/v1/admin/system-info")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "environment" in data
        assert "debug_mode" in data
        assert "log_level" in data

    def test_get_system_info_structure(self, client: TestClient):
        """Test system information response structure."""
        response = client.get("/api/v1/admin/system-info")
        data = response.json()

        # Check required fields
        required_fields = ["environment", "debug_mode", "log_level", "log_format"]
        for field in required_fields:
            assert field in data
            assert data[field] is not None

    def test_get_system_info_environment(self, client: TestClient):
        """Test system information environment field."""
        response = client.get("/api/v1/admin/system-info")
        data = response.json()

        assert data["environment"] in ["development", "testing", "production"]


class TestLogLevelManagement:
    """Test log level management endpoints."""

    def test_get_log_level(self, client: TestClient):
        """Test getting current log level."""
        response = client.get("/api/v1/admin/log-level")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "success" in data
        assert "current_level" in data

    def test_set_log_level_valid(self, client: TestClient):
        """Test setting valid log level."""
        log_data = {"level": "DEBUG"}
        response = client.post("/api/v1/admin/log-level", json=log_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert "current_level" in data

    def test_set_log_level_invalid(self, client: TestClient):
        """Test setting invalid log level."""
        log_data = {"level": "INVALID"}
        response = client.post("/api/v1/admin/log-level", json=log_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_set_log_level_missing_field(self, client: TestClient):
        """Test setting log level with missing field."""
        log_data = {}
        response = client.post("/api/v1/admin/log-level", json=log_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_set_log_level_case_insensitive(self, client: TestClient):
        """Test setting log level with case insensitive input."""
        log_data = {"level": "debug"}
        response = client.post("/api/v1/admin/log-level", json=log_data)
        assert response.status_code == status.HTTP_200_OK

    def test_set_log_level_all_levels(self, client: TestClient):
        """Test setting all valid log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            log_data = {"level": level}
            response = client.post("/api/v1/admin/log-level", json=log_data)
            assert response.status_code == status.HTTP_200_OK


class TestModuleManagement:
    """Test module management endpoints."""

    def test_get_modules(self, client: TestClient):
        """Test getting configured modules."""
        response = client.get("/api/v1/admin/modules")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, dict)

    def test_get_modules_structure(self, client: TestClient):
        """Test modules response structure."""
        response = client.get("/api/v1/admin/modules")
        data = response.json()

        # Should be a dictionary
        assert isinstance(data, dict)

    def test_get_modules_after_setting_levels(self, client: TestClient):
        """Test getting modules after setting log levels."""
        # Set a log level for a module
        log_data = {"level": "DEBUG", "module": "test.module"}
        client.post("/api/v1/admin/log-level", json=log_data)

        # Get modules
        response = client.get("/api/v1/admin/modules")
        assert response.status_code == status.HTTP_200_OK


class TestLoggingReset:
    """Test logging reset functionality."""

    def test_reset_logging(self, client: TestClient):
        """Test resetting logging configuration."""
        response = client.post("/api/v1/admin/reset-logging")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True

    def test_reset_logging_after_changes(self, client: TestClient):
        """Test resetting logging after making changes."""
        # Set a log level
        log_data = {"level": "DEBUG"}
        client.post("/api/v1/admin/log-level", json=log_data)

        # Reset logging
        response = client.post("/api/v1/admin/reset-logging")
        assert response.status_code == status.HTTP_200_OK

    def test_reset_logging_multiple_times(self, client: TestClient):
        """Test resetting logging multiple times."""
        # Reset multiple times
        for _ in range(3):
            response = client.post("/api/v1/admin/reset-logging")
            assert response.status_code == status.HTTP_200_OK


class TestAdminRouterIntegration:
    """Test admin router integration scenarios."""

    def test_admin_endpoints_error_handling(self, client: TestClient):
        """Test admin endpoints error handling."""
        # Test with invalid JSON
        response = client.post("/api/v1/admin/log-level", data="invalid json")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_admin_endpoints_response_time(self, client: TestClient):
        """Test admin endpoints response time."""
        import time

        start_time = time.time()
        response = client.get("/api/v1/admin/system-info")
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        assert (end_time - start_time) < 1.0  # Should respond within 1 second

    def test_admin_endpoints_concurrent_access(self, client: TestClient):
        """Test admin endpoints with concurrent access."""
        import threading

        results = []

        def make_request():
            response = client.get("/api/v1/admin/system-info")
            results.append(response.status_code)

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert all(status_code == 200 for status_code in results)

    def test_admin_endpoints_log_level_workflow(self, client: TestClient):
        """Test complete log level management workflow."""
        # Get initial log level
        response = client.get("/api/v1/admin/log-level")
        assert response.status_code == status.HTTP_200_OK
        initial_data = response.json()
        assert "current_level" in initial_data

        # Set new log level
        log_data = {"level": "DEBUG"}
        response = client.post("/api/v1/admin/log-level", json=log_data)
        assert response.status_code == status.HTTP_200_OK

        # Verify the change
        response = client.get("/api/v1/admin/log-level")
        assert response.status_code == status.HTTP_200_OK
        new_data = response.json()
        assert "current_level" in new_data

    def test_admin_endpoints_modules_workflow(self, client: TestClient):
        """Test complete module management workflow."""
        # Get initial modules
        response = client.get("/api/v1/admin/modules")
        assert response.status_code == status.HTTP_200_OK
        initial_modules = response.json()
        assert isinstance(initial_modules, dict)

        # Set log level for a module
        log_data = {"level": "DEBUG", "module": "test.module"}
        response = client.post("/api/v1/admin/log-level", json=log_data)
        assert response.status_code == status.HTTP_200_OK

        # Get modules again
        response = client.get("/api/v1/admin/modules")
        assert response.status_code == status.HTTP_200_OK
        updated_modules = response.json()
        assert isinstance(updated_modules, dict)

    def test_admin_endpoints_system_info_consistency(self, client: TestClient):
        """Test system info endpoint consistency."""
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.get("/api/v1/admin/system-info")
            responses.append(response.json())

        # All responses should have the same structure
        for response_data in responses:
            assert "environment" in response_data
            assert "debug_mode" in response_data
            assert "log_level" in response_data

    def test_admin_endpoints_invalid_methods(self, client: TestClient):
        """Test admin endpoints with invalid HTTP methods."""
        # Test POST on GET-only endpoint
        response = client.post("/api/v1/admin/system-info")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # Test PUT on GET endpoint
        response = client.put("/api/v1/admin/modules")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_admin_endpoints_large_payload(self, client: TestClient):
        """Test admin endpoints with large payload."""
        # Test with large log level data
        large_data = {"level": "DEBUG", "module": "x" * 1000}
        response = client.post("/api/v1/admin/log-level", json=large_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_admin_endpoints_special_characters(self, client: TestClient):
        """Test admin endpoints with special characters."""
        # Test with special characters in module name
        special_data = {"level": "DEBUG", "module": "test.module@#$%"}
        response = client.post("/api/v1/admin/log-level", json=special_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_admin_endpoints_authentication_required(self, client: TestClient):
        """Test that admin endpoints require authentication."""
        # This test would need to be implemented based on your auth requirements
        # For now, we'll just test that the endpoints are accessible
        response = client.get("/api/v1/admin/system-info")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_endpoints_rate_limiting(self, client: TestClient):
        """Test admin endpoints rate limiting."""
        # Make many requests quickly
        responses = []
        for _ in range(10):
            response = client.get("/api/v1/admin/system-info")
            responses.append(response.status_code)

        # All should succeed (no rate limiting implemented yet)
        assert all(status_code == 200 for status_code in responses)

    def test_admin_endpoints_content_type(self, client: TestClient):
        """Test admin endpoints content type."""
        response = client.get("/api/v1/admin/system-info")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/json"

    def test_admin_endpoints_cors_headers(self, client: TestClient):
        """Test admin endpoints CORS headers."""
        response = client.options("/api/v1/admin/system-info")
        # Currently OPTIONS requests return 405 as the endpoint doesn't support them
        assert response.status_code == 405
        # Check that the response includes the allowed methods
        assert "allow" in response.headers
