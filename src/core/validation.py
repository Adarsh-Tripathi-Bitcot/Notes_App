"""
Enhanced input validation utilities.

This module provides comprehensive input validation functions
for functional arguments and API endpoints.
"""

import re
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Custom validation error with detailed information."""

    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.field = field
        self.details = details or {}
        super().__init__(self.message)


def validate_email(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Validated email address

    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError("Email is required", field="email")

    # Basic email regex pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_pattern, email):
        raise ValidationError(
            "Invalid email format",
            field="email",
            details={"provided": email, "expected_format": "user@domain.com"},
        )

    # Check length
    if len(email) > 254:
        raise ValidationError(
            "Email too long",
            field="email",
            details={"max_length": 254, "provided_length": len(email)},
        )

    return email.lower().strip()


def validate_password(password: str) -> str:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Validated password

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if not password:
        raise ValidationError("Password is required", field="password")

    # Check minimum length
    if len(password) < 8:
        raise ValidationError(
            "Password too short",
            field="password",
            details={"min_length": 8, "provided_length": len(password)},
        )

    # Check maximum length
    if len(password) > 128:
        raise ValidationError(
            "Password too long",
            field="password",
            details={"max_length": 128, "provided_length": len(password)},
        )

    # Check for at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        raise ValidationError(
            "Password must contain at least one uppercase letter", field="password"
        )

    # Check for at least one lowercase letter
    if not re.search(r"[a-z]", password):
        raise ValidationError(
            "Password must contain at least one lowercase letter", field="password"
        )

    # Check for at least one digit
    if not re.search(r"\d", password):
        raise ValidationError(
            "Password must contain at least one digit", field="password"
        )

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(
            "Password must contain at least one special character", field="password"
        )

    return password


def validate_username(username: str) -> str:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        Validated username

    Raises:
        ValidationError: If username format is invalid
    """
    if not username:
        raise ValidationError("Username is required", field="username")

    # Check length
    if len(username) < 3:
        raise ValidationError(
            "Username too short",
            field="username",
            details={"min_length": 3, "provided_length": len(username)},
        )

    if len(username) > 30:
        raise ValidationError(
            "Username too long",
            field="username",
            details={"max_length": 30, "provided_length": len(username)},
        )

    # Check for valid characters (alphanumeric and underscore only)
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise ValidationError(
            "Username can only contain letters, numbers, and underscores",
            field="username",
        )

    # Check that it doesn't start with a number
    if username[0].isdigit():
        raise ValidationError("Username cannot start with a number", field="username")

    return username.lower().strip()


def validate_string_field(
    value: Any,
    field_name: str,
    min_length: int = 1,
    max_length: int = 255,
    allow_empty: bool = False,
) -> str:
    """
    Validate string field with length constraints.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_length: Minimum length
        max_length: Maximum length
        allow_empty: Whether to allow empty strings

    Returns:
        Validated string

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        if allow_empty:
            return ""
        raise ValidationError(f"{field_name} is required", field=field_name)

    if not isinstance(value, str):
        raise ValidationError(
            f"{field_name} must be a string",
            field=field_name,
            details={"provided_type": type(value).__name__},
        )

    value = value.strip()

    if not value and not allow_empty:
        raise ValidationError(f"{field_name} cannot be empty", field=field_name)

    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} too short",
            field=field_name,
            details={"min_length": min_length, "provided_length": len(value)},
        )

    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} too long",
            field=field_name,
            details={"max_length": max_length, "provided_length": len(value)},
        )

    return value


def validate_positive_integer(
    value: Any, field_name: str, min_value: int = 1, max_value: Optional[int] = None
) -> int:
    """
    Validate positive integer field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Validated integer

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        raise ValidationError(f"{field_name} is required", field=field_name)

    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"{field_name} must be an integer",
            field=field_name,
            details={"provided_type": type(value).__name__},
        )

    if int_value < min_value:
        raise ValidationError(
            f"{field_name} must be at least {min_value}",
            field=field_name,
            details={"min_value": min_value, "provided_value": int_value},
        )

    if max_value is not None and int_value > max_value:
        raise ValidationError(
            f"{field_name} must be at most {max_value}",
            field=field_name,
            details={"max_value": max_value, "provided_value": int_value},
        )

    return int_value


def validate_boolean(value: Any, field_name: str) -> bool:
    """
    Validate boolean field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated boolean

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        raise ValidationError(f"{field_name} is required", field=field_name)

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        if value.lower() in ["true", "1", "yes", "on"]:
            return True
        elif value.lower() in ["false", "0", "no", "off"]:
            return False

    raise ValidationError(
        f"{field_name} must be a boolean",
        field=field_name,
        details={"provided_type": type(value).__name__},
    )


def validate_enum_value(value: Any, field_name: str, allowed_values: List[str]) -> str:
    """
    Validate enum-like field.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        allowed_values: List of allowed values

    Returns:
        Validated value

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        raise ValidationError(f"{field_name} is required", field=field_name)

    if not isinstance(value, str):
        raise ValidationError(
            f"{field_name} must be a string",
            field=field_name,
            details={"provided_type": type(value).__name__},
        )

    value = value.strip()

    if value not in allowed_values:
        raise ValidationError(
            f"{field_name} must be one of: {', '.join(allowed_values)}",
            field=field_name,
            details={"allowed_values": allowed_values, "provided_value": value},
        )

    return value


class ValidationResult:
    """Result of validation operation."""

    def __init__(self, is_valid: bool, errors: List[ValidationError] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, error: ValidationError):
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False

    def get_error_messages(self) -> List[str]:
        """Get list of error messages."""
        return [error.message for error in self.errors]

    def get_errors_by_field(self) -> Dict[str, List[str]]:
        """Get errors grouped by field name."""
        errors_by_field = {}
        for error in self.errors:
            field = error.field or "general"
            if field not in errors_by_field:
                errors_by_field[field] = []
            errors_by_field[field].append(error.message)
        return errors_by_field


def validate_dict_fields(
    data: Dict[str, Any], validation_rules: Dict[str, Dict[str, Any]]
) -> ValidationResult:
    """
    Validate multiple fields in a dictionary.

    Args:
        data: Dictionary to validate
        validation_rules: Rules for each field

    Returns:
        ValidationResult with validation status and errors
    """
    result = ValidationResult(True)

    for field_name, rules in validation_rules.items():
        try:
            value = data.get(field_name)

            # Check if field is required
            if rules.get("required", False) and value is None:
                result.add_error(
                    ValidationError(f"{field_name} is required", field=field_name)
                )
                continue

            # Skip validation if field is not required and not provided
            if not rules.get("required", False) and value is None:
                continue

            # Apply validation based on field type
            field_type = rules.get("type", "string")

            if field_type == "email":
                validate_email(value)
            elif field_type == "password":
                validate_password(value)
            elif field_type == "username":
                validate_username(value)
            elif field_type == "string":
                validate_string_field(
                    value,
                    field_name,
                    min_length=rules.get("min_length", 1),
                    max_length=rules.get("max_length", 255),
                    allow_empty=rules.get("allow_empty", False),
                )
            elif field_type == "integer":
                validate_positive_integer(
                    value,
                    field_name,
                    min_value=rules.get("min_value", 1),
                    max_value=rules.get("max_value"),
                )
            elif field_type == "boolean":
                validate_boolean(value, field_name)
            elif field_type == "enum":
                validate_enum_value(value, field_name, rules.get("allowed_values", []))

        except ValidationError as e:
            result.add_error(e)

    return result
