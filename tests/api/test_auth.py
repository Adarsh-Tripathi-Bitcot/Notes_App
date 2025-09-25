"""
API tests for authentication endpoints.

This module contains tests for user registration, login, and authentication
functionality in the Notes App API.
"""

from fastapi.testclient import TestClient


class TestUserRegistration:
    """Test user registration functionality."""

    def test_register_user_success(self, client: TestClient, sample_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert "id" in data
        assert "created_at" in data
        assert "hashed_password" not in data  # Password should not be returned

    def test_register_user_duplicate_email(
        self, client: TestClient, test_user, sample_user_data
    ):
        """Test registration with duplicate email."""
        # Use the same email as the test user
        sample_user_data["email"] = test_user.email

        response = client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_register_user_duplicate_username(
        self, client: TestClient, test_user, sample_user_data
    ):
        """Test registration with duplicate username."""
        # Use the same username as the test user
        sample_user_data["username"] = test_user.username

        response = client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_register_user_invalid_email(self, client: TestClient, sample_user_data):
        """Test registration with invalid email format."""
        sample_user_data["email"] = "invalid-email"

        response = client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_register_user_weak_password(self, client: TestClient, sample_user_data):
        """Test registration with weak password."""
        sample_user_data["password"] = "123"  # Too short

        response = client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_register_user_password_mismatch(
        self, client: TestClient, sample_user_data
    ):
        """Test registration with mismatched passwords."""
        sample_user_data["confirm_password"] = "differentpassword"

        response = client.post("/api/v1/users/register", json=sample_user_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_register_user_missing_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        incomplete_data = {"email": "test@example.com"}

        response = client.post("/api/v1/users/register", json=incomplete_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data


class TestUserLogin:
    """Test user login functionality."""

    def test_login_success(self, client: TestClient, test_user, sample_login_data):
        """Test successful user login."""
        response = client.post("/api/v1/users/login", json=sample_login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email."""
        login_data = {"email": "nonexistent@example.com", "password": "testpassword123"}

        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_login_invalid_password(self, client: TestClient, test_user):
        """Test login with incorrect password."""
        login_data = {"email": test_user.email, "password": "wrongpassword"}

        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_login_inactive_user(self, client: TestClient, db_session, test_user):
        """Test login with inactive user."""
        # Deactivate the test user
        test_user.is_active = False
        db_session.commit()

        login_data = {"email": test_user.email, "password": "testpassword123"}

        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields."""
        incomplete_data = {"email": "test@example.com"}

        response = client.post("/api/v1/users/login", json=incomplete_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data


class TestUserProfile:
    """Test user profile functionality."""

    def test_get_current_user_profile(self, client: TestClient, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "created_at" in data

    def test_get_profile_without_auth(self, client: TestClient):
        """Test getting profile without authentication."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 403
        data = response.json()
        assert "error" in data

    def test_get_profile_invalid_token(self, client: TestClient):
        """Test getting profile with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_update_user_profile(self, client: TestClient, auth_headers):
        """Test updating user profile."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio",
        }

        response = client.put(
            "/api/v1/users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert data["bio"] == update_data["bio"]

    def test_update_profile_without_auth(self, client: TestClient):
        """Test updating profile without authentication."""
        update_data = {"first_name": "Updated"}

        response = client.put("/api/v1/users/me", json=update_data)

        assert response.status_code == 403
        data = response.json()
        assert "error" in data


class TestPasswordChange:
    """Test password change functionality."""

    def test_change_password_success(self, client: TestClient, auth_headers):
        """Test successful password change."""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        }

        response = client.put(
            "/api/v1/users/me/password", json=password_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_change_password_wrong_current(self, client: TestClient, auth_headers):
        """Test password change with wrong current password."""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        }

        response = client.put(
            "/api/v1/users/me/password", json=password_data, headers=auth_headers
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_change_password_mismatch(self, client: TestClient, auth_headers):
        """Test password change with mismatched new passwords."""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword",
        }

        response = client.put(
            "/api/v1/users/me/password", json=password_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_change_password_weak_new(self, client: TestClient, auth_headers):
        """Test password change with weak new password."""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "123",
            "confirm_password": "123",
        }

        response = client.put(
            "/api/v1/users/me/password", json=password_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data


class TestUserStats:
    """Test user statistics functionality."""

    def test_get_user_stats(self, client: TestClient, auth_headers):
        """Test getting user statistics."""
        response = client.get("/api/v1/users/me/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_notes" in data
        assert "active_notes" in data
        assert "archived_notes" in data
        assert "created_at" in data
        assert "last_login" in data

    def test_get_stats_without_auth(self, client: TestClient):
        """Test getting stats without authentication."""
        response = client.get("/api/v1/users/me/stats")

        assert response.status_code == 403
        data = response.json()
        assert "error" in data


class TestLogout:
    """Test logout functionality."""

    def test_logout_success(self, client: TestClient, auth_headers):
        """Test successful logout."""
        response = client.post("/api/v1/users/logout", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_logout_without_auth(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/api/v1/users/logout")

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
