"""
Pydantic schemas for user-related data validation.

This module defines Pydantic models for user data validation,
serialization, and API request/response handling.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """
    Base user schema with common fields.

    This schema contains fields that are common to all user-related schemas.
    """

    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="First name"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Last name"
    )
    bio: Optional[str] = Field(None, max_length=500, description="User biography")

    @validator("username")
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format."""
        if v is not None:
            if not v.replace("_", "").replace("-", "").isalnum():
                raise ValueError(
                    "Username can only contain letters, numbers, "
                    "underscores, and hyphens"
                )
            if v.startswith(("_", "-")) or v.endswith(("_", "-")):
                raise ValueError(
                    "Username cannot start or end with underscore or hyphen"
                )
        return v


class UserCreate(UserBase):
    """
    Schema for user creation.

    This schema is used for user registration requests.
    """

    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )
    confirm_password: str = Field(..., description="Password confirmation")

    @validator("password")
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v

    @validator("confirm_password")
    def validate_confirm_password(cls, v: str, values: dict) -> str:
        """Validate password confirmation."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserUpdate(BaseModel):
    """
    Schema for user updates.

    This schema is used for updating user information.
    """

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="First name"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Last name"
    )
    bio: Optional[str] = Field(None, max_length=500, description="User biography")

    @validator("username")
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format."""
        if v is not None:
            if not v.replace("_", "").replace("-", "").isalnum():
                raise ValueError(
                    "Username can only contain letters, numbers, "
                    "underscores, and hyphens"
                )
            if v.startswith(("_", "-")) or v.endswith(("_", "-")):
                raise ValueError(
                    "Username cannot start or end with underscore or hyphen"
                )
        return v


class UserPasswordUpdate(BaseModel):
    """
    Schema for password updates.

    This schema is used for changing user passwords.
    """

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )
    confirm_password: str = Field(..., description="Password confirmation")

    @validator("new_password")
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v

    @validator("confirm_password")
    def validate_confirm_password(cls, v: str, values: dict) -> str:
        """Validate password confirmation."""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponse(UserBase):
    """
    Schema for user responses.

    This schema is used for returning user data in API responses.
    """

    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether the user is active")
    is_verified: bool = Field(..., description="Whether the user is verified")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class UserProfile(UserResponse):
    """
    Schema for user profile information.

    This schema includes additional computed fields for user profiles.
    """

    full_name: str = Field(..., description="User's full name")
    display_name: str = Field(..., description="User's display name")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserLogin(BaseModel):
    """
    Schema for user login.

    This schema is used for user authentication requests.
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """
    Schema for token responses.

    This schema is used for returning authentication tokens.
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserStats(BaseModel):
    """
    Schema for user statistics.

    This schema is used for returning user-related statistics.
    """

    total_notes: int = Field(..., description="Total number of notes")
    active_notes: int = Field(..., description="Number of active notes")
    archived_notes: int = Field(..., description="Number of archived notes")
    created_at: datetime = Field(..., description="User creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
