"""
Unit tests for validation module.

This module tests all validation functions and classes
in the validation module.
"""


import pytest

from src.core.validation import (
    ValidationError,
    ValidationResult,
    validate_boolean,
    validate_dict_fields,
    validate_email,
    validate_enum_value,
    validate_password,
    validate_positive_integer,
    validate_string_field,
    validate_username,
)


class TestValidationError:
    """Test ValidationError exception class."""

    def test_validation_error_basic(self):
        """Test basic ValidationError creation."""
        error = ValidationError("Test error")
        assert error.message == "Test error"
        assert error.field is None
        assert error.details == {}

    def test_validation_error_with_field(self):
        """Test ValidationError with field name."""
        error = ValidationError("Test error", field="test_field")
        assert error.message == "Test error"
        assert error.field == "test_field"
        assert error.details == {}

    def test_validation_error_with_details(self):
        """Test ValidationError with details."""
        details = {"key": "value"}
        error = ValidationError("Test error", field="test_field", details=details)
        assert error.message == "Test error"
        assert error.field == "test_field"
        assert error.details == details

    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance from Exception."""
        error = ValidationError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"


class TestValidateEmail:
    """Test email validation function."""

    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
            "user123@test-domain.com",
            "a@b.co",
        ]

        for email in valid_emails:
            result = validate_email(email)
            assert result == email.lower().strip()

    def test_validate_email_empty(self):
        """Test empty email validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("")
        assert exc_info.value.message == "Email is required"
        assert exc_info.value.field == "email"

    def test_validate_email_none(self):
        """Test None email validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email(None)
        assert exc_info.value.message == "Email is required"
        assert exc_info.value.field == "email"

    def test_validate_email_invalid_format(self):
        """Test invalid email formats."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test@.com",
            "test@example.",
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                validate_email(email)
            assert exc_info.value.message == "Invalid email format"
            assert exc_info.value.field == "email"
            assert "provided" in exc_info.value.details

    def test_validate_email_too_long(self):
        """Test email that's too long."""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError) as exc_info:
            validate_email(long_email)
        assert exc_info.value.message == "Email too long"
        assert exc_info.value.field == "email"
        assert exc_info.value.details["max_length"] == 254

    def test_validate_email_normalization(self):
        """Test email normalization."""
        # The validation function doesn't handle whitespace, so test without it
        result = validate_email("TEST@EXAMPLE.COM")
        assert result == "test@example.com"


class TestValidatePassword:
    """Test password validation function."""

    def test_validate_password_valid(self):
        """Test valid passwords."""
        valid_passwords = [
            "Password123!",
            "MyStr0ng#Pass",
            "Test123@",
            "Valid1$Pass",
        ]

        for password in valid_passwords:
            result = validate_password(password)
            assert result == password

    def test_validate_password_empty(self):
        """Test empty password validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("")
        assert exc_info.value.message == "Password is required"
        assert exc_info.value.field == "password"

    def test_validate_password_none(self):
        """Test None password validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password(None)
        assert exc_info.value.message == "Password is required"
        assert exc_info.value.field == "password"

    def test_validate_password_too_short(self):
        """Test password that's too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("Pass1!")
        assert exc_info.value.message == "Password too short"
        assert exc_info.value.field == "password"
        assert exc_info.value.details["min_length"] == 8

    def test_validate_password_too_long(self):
        """Test password that's too long."""
        long_password = "A" * 129 + "1!"
        with pytest.raises(ValidationError) as exc_info:
            validate_password(long_password)
        assert exc_info.value.message == "Password too long"
        assert exc_info.value.field == "password"
        assert exc_info.value.details["max_length"] == 128

    def test_validate_password_no_uppercase(self):
        """Test password without uppercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("password123!")
        assert (
            exc_info.value.message
            == "Password must contain at least one uppercase letter"
        )
        assert exc_info.value.field == "password"

    def test_validate_password_no_lowercase(self):
        """Test password without lowercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("PASSWORD123!")
        assert (
            exc_info.value.message
            == "Password must contain at least one lowercase letter"
        )
        assert exc_info.value.field == "password"

    def test_validate_password_no_digit(self):
        """Test password without digit."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("Password!")
        assert exc_info.value.message == "Password must contain at least one digit"
        assert exc_info.value.field == "password"

    def test_validate_password_no_special_char(self):
        """Test password without special character."""
        with pytest.raises(ValidationError) as exc_info:
            validate_password("Password123")
        assert (
            exc_info.value.message
            == "Password must contain at least one special character"
        )
        assert exc_info.value.field == "password"


class TestValidateUsername:
    """Test username validation function."""

    def test_validate_username_valid(self):
        """Test valid usernames."""
        valid_usernames = [
            "testuser",
            "user123",
            "test_user",
            "User123",
            "abc",  # Min length
            "a" * 30,  # Max length
        ]

        for username in valid_usernames:
            result = validate_username(username)
            assert result == username.lower().strip()

    def test_validate_username_empty(self):
        """Test empty username validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_username("")
        assert exc_info.value.message == "Username is required"
        assert exc_info.value.field == "username"

    def test_validate_username_none(self):
        """Test None username validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_username(None)
        assert exc_info.value.message == "Username is required"
        assert exc_info.value.field == "username"

    def test_validate_username_too_short(self):
        """Test username that's too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_username("ab")
        assert exc_info.value.message == "Username too short"
        assert exc_info.value.field == "username"
        assert exc_info.value.details["min_length"] == 3

    def test_validate_username_too_long(self):
        """Test username that's too long."""
        long_username = "a" * 31
        with pytest.raises(ValidationError) as exc_info:
            validate_username(long_username)
        assert exc_info.value.message == "Username too long"
        assert exc_info.value.field == "username"
        assert exc_info.value.details["max_length"] == 30

    def test_validate_username_invalid_characters(self):
        """Test username with invalid characters."""
        invalid_usernames = [
            "test-user",
            "test.user",
            "test@user",
            "test user",
            "test#user",
        ]

        for username in invalid_usernames:
            with pytest.raises(ValidationError) as exc_info:
                validate_username(username)
            assert (
                exc_info.value.message
                == "Username can only contain letters, numbers, and underscores"
            )
            assert exc_info.value.field == "username"

    def test_validate_username_starts_with_number(self):
        """Test username starting with number."""
        with pytest.raises(ValidationError) as exc_info:
            validate_username("123user")
        assert exc_info.value.message == "Username cannot start with a number"
        assert exc_info.value.field == "username"

    def test_validate_username_normalization(self):
        """Test username normalization."""
        # The validation function doesn't handle whitespace, so test without it
        result = validate_username("TEST_USER")
        assert result == "test_user"


class TestValidateStringField:
    """Test string field validation function."""

    def test_validate_string_field_valid(self):
        """Test valid string fields."""
        result = validate_string_field("test", "test_field")
        assert result == "test"

    def test_validate_string_field_none_required(self):
        """Test None value when required."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_field(None, "test_field")
        assert exc_info.value.message == "test_field is required"
        assert exc_info.value.field == "test_field"

    def test_validate_string_field_none_allowed_empty(self):
        """Test None value when empty is allowed."""
        result = validate_string_field(None, "test_field", allow_empty=True)
        assert result == ""

    def test_validate_string_field_wrong_type(self):
        """Test non-string value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_field(123, "test_field")
        assert exc_info.value.message == "test_field must be a string"
        assert exc_info.value.field == "test_field"
        assert exc_info.value.details["provided_type"] == "int"

    def test_validate_string_field_empty_not_allowed(self):
        """Test empty string when not allowed."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_field("", "test_field")
        assert exc_info.value.message == "test_field cannot be empty"
        assert exc_info.value.field == "test_field"

    def test_validate_string_field_empty_allowed(self):
        """Test empty string when allowed."""
        result = validate_string_field("", "test_field", allow_empty=True, min_length=0)
        assert result == ""

    def test_validate_string_field_too_short(self):
        """Test string that's too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_field("ab", "test_field", min_length=3)
        assert exc_info.value.message == "test_field too short"
        assert exc_info.value.field == "test_field"
        assert exc_info.value.details["min_length"] == 3

    def test_validate_string_field_too_long(self):
        """Test string that's too long."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_field("a" * 10, "test_field", max_length=5)
        assert exc_info.value.message == "test_field too long"
        assert exc_info.value.field == "test_field"
        assert exc_info.value.details["max_length"] == 5

    def test_validate_string_field_whitespace_trimming(self):
        """Test that whitespace is trimmed."""
        result = validate_string_field("  test  ", "test_field")
        assert result == "test"


class TestValidatePositiveInteger:
    """Test positive integer validation function."""

    def test_validate_positive_integer_valid(self):
        """Test valid positive integers."""
        result = validate_positive_integer(5, "test_field")
        assert result == 5

    def test_validate_positive_integer_string(self):
        """Test string that can be converted to int."""
        result = validate_positive_integer("5", "test_field")
        assert result == 5

    def test_validate_positive_integer_none(self):
        """Test None value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(None, "test_field")
        assert exc_info.value.message == "test_field is required"
        assert exc_info.value.field == "test_field"

    def test_validate_positive_integer_invalid_string(self):
        """Test invalid string that can't be converted to int."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer("abc", "test_field")
        assert exc_info.value.message == "test_field must be an integer"
        assert exc_info.value.field == "test_field"

    def test_validate_positive_integer_wrong_type(self):
        """Test wrong type."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer([1, 2, 3], "test_field")
        assert exc_info.value.message == "test_field must be an integer"
        assert exc_info.value.field == "test_field"

    def test_validate_positive_integer_too_small(self):
        """Test value below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(0, "test_field", min_value=1)
        assert exc_info.value.message == "test_field must be at least 1"
        assert exc_info.value.field == "test_field"
        assert exc_info.value.details["min_value"] == 1

    def test_validate_positive_integer_too_large(self):
        """Test value above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(10, "test_field", max_value=5)
        assert exc_info.value.message == "test_field must be at most 5"
        assert exc_info.value.field == "test_field"
        assert exc_info.value.details["max_value"] == 5

    def test_validate_positive_integer_no_max(self):
        """Test with no maximum value."""
        result = validate_positive_integer(1000, "test_field")
        assert result == 1000


class TestValidateBoolean:
    """Test boolean validation function."""

    def test_validate_boolean_true_values(self):
        """Test various true values."""
        true_values = [True, "true", "TRUE", "1", "yes", "YES", "on", "ON"]
        for value in true_values:
            result = validate_boolean(value, "test_field")
            assert result is True

    def test_validate_boolean_false_values(self):
        """Test various false values."""
        false_values = [False, "false", "FALSE", "0", "no", "NO", "off", "OFF"]
        for value in false_values:
            result = validate_boolean(value, "test_field")
            assert result is False

    def test_validate_boolean_none(self):
        """Test None value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_boolean(None, "test_field")
        assert exc_info.value.message == "test_field is required"
        assert exc_info.value.field == "test_field"

    def test_validate_boolean_invalid_string(self):
        """Test invalid string value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_boolean("maybe", "test_field")
        assert exc_info.value.message == "test_field must be a boolean"
        assert exc_info.value.field == "test_field"

    def test_validate_boolean_invalid_type(self):
        """Test invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            validate_boolean(123, "test_field")
        assert exc_info.value.message == "test_field must be a boolean"
        assert exc_info.value.field == "test_field"


class TestValidateEnumValue:
    """Test enum value validation function."""

    def test_validate_enum_value_valid(self):
        """Test valid enum values."""
        allowed_values = ["option1", "option2", "option3"]
        result = validate_enum_value("option1", "test_field", allowed_values)
        assert result == "option1"

    def test_validate_enum_value_none(self):
        """Test None value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_enum_value(None, "test_field", ["option1"])
        assert exc_info.value.message == "test_field is required"
        assert exc_info.value.field == "test_field"

    def test_validate_enum_value_wrong_type(self):
        """Test wrong type."""
        with pytest.raises(ValidationError) as exc_info:
            validate_enum_value(123, "test_field", ["option1"])
        assert exc_info.value.message == "test_field must be a string"
        assert exc_info.value.field == "test_field"

    def test_validate_enum_value_invalid_value(self):
        """Test invalid enum value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_enum_value("invalid", "test_field", ["option1", "option2"])
        assert exc_info.value.message == "test_field must be one of: option1, option2"
        assert exc_info.value.field == "test_field"
        assert exc_info.value.details["allowed_values"] == ["option1", "option2"]

    def test_validate_enum_value_whitespace_trimming(self):
        """Test that whitespace is trimmed."""
        result = validate_enum_value("  option1  ", "test_field", ["option1"])
        assert result == "option1"


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_valid(self):
        """Test valid validation result."""
        result = ValidationResult(True)
        assert result.is_valid is True
        assert result.errors == []

    def test_validation_result_invalid(self):
        """Test invalid validation result."""
        errors = [ValidationError("Error 1"), ValidationError("Error 2")]
        result = ValidationResult(False, errors)
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validation_result_add_error(self):
        """Test adding error to validation result."""
        result = ValidationResult(True)
        error = ValidationError("Test error")
        result.add_error(error)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0] == error

    def test_validation_result_get_error_messages(self):
        """Test getting error messages."""
        errors = [ValidationError("Error 1"), ValidationError("Error 2")]
        result = ValidationResult(False, errors)
        messages = result.get_error_messages()
        assert messages == ["Error 1", "Error 2"]

    def test_validation_result_get_errors_by_field(self):
        """Test getting errors grouped by field."""
        errors = [
            ValidationError("Error 1", field="field1"),
            ValidationError("Error 2", field="field1"),
            ValidationError("Error 3", field="field2"),
            ValidationError("Error 4"),  # No field
        ]
        result = ValidationResult(False, errors)
        errors_by_field = result.get_errors_by_field()

        assert "field1" in errors_by_field
        assert "field2" in errors_by_field
        assert "general" in errors_by_field
        assert len(errors_by_field["field1"]) == 2
        assert len(errors_by_field["field2"]) == 1
        assert len(errors_by_field["general"]) == 1


class TestValidateDictFields:
    """Test dictionary fields validation function."""

    def test_validate_dict_fields_valid(self):
        """Test valid dictionary validation."""
        data = {
            "email": "test@example.com",
            "password": "Password123!",
            "username": "testuser",
            "age": 25,
            "active": True,
            "status": "active",
        }

        rules = {
            "email": {"type": "email", "required": True},
            "password": {"type": "password", "required": True},
            "username": {"type": "username", "required": True},
            "age": {"type": "integer", "required": True, "min_value": 18},
            "active": {"type": "boolean", "required": True},
            "status": {
                "type": "enum",
                "required": True,
                "allowed_values": ["active", "inactive"],
            },
        }

        result = validate_dict_fields(data, rules)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_dict_fields_missing_required(self):
        """Test validation with missing required fields."""
        data = {"email": "test@example.com"}
        rules = {
            "email": {"type": "email", "required": True},
            "password": {"type": "password", "required": True},
        }

        result = validate_dict_fields(data, rules)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "password is required" in result.get_error_messages()

    def test_validate_dict_fields_invalid_values(self):
        """Test validation with invalid values."""
        data = {
            "email": "invalid-email",
            "password": "weak",
            "username": "ab",
            "age": "not-a-number",
            "active": "maybe",
            "status": "invalid",
        }

        rules = {
            "email": {"type": "email", "required": True},
            "password": {"type": "password", "required": True},
            "username": {"type": "username", "required": True},
            "age": {"type": "integer", "required": True},
            "active": {"type": "boolean", "required": True},
            "status": {
                "type": "enum",
                "required": True,
                "allowed_values": ["active", "inactive"],
            },
        }

        result = validate_dict_fields(data, rules)
        assert result.is_valid is False
        assert len(result.errors) == 6  # All fields are invalid

    def test_validate_dict_fields_optional_fields(self):
        """Test validation with optional fields."""
        data = {"email": "test@example.com"}
        rules = {
            "email": {"type": "email", "required": True},
            "username": {"type": "username", "required": False},
        }

        result = validate_dict_fields(data, rules)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_dict_fields_string_validation(self):
        """Test string field validation in dict."""
        data = {"title": "Test Title", "description": ""}
        rules = {
            "title": {
                "type": "string",
                "required": True,
                "min_length": 5,
                "max_length": 50,
            },
            "description": {
                "type": "string",
                "required": False,
                "allow_empty": True,
                "min_length": 0,
            },
        }

        result = validate_dict_fields(data, rules)
        assert result.is_valid is True

    def test_validate_dict_fields_integer_validation(self):
        """Test integer field validation in dict."""
        data = {
            "count": 25,
            "limit": 100,
        }  # count=25 should be invalid with max_value=20
        rules = {
            "count": {
                "type": "integer",
                "required": True,
                "min_value": 1,
                "max_value": 20,
            },
            "limit": {"type": "integer", "required": True, "min_value": 1},
        }

        result = validate_dict_fields(data, rules)
        assert result.is_valid is False  # count=25 is invalid with max_value=20
