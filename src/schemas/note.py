"""
Pydantic schemas for note-related data validation.

This module defines Pydantic models for note data validation,
serialization, and API request/response handling.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class NoteStatus(str, Enum):
    """Enumeration for note status values."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class NoteBase(BaseModel):
    """
    Base note schema with common fields.

    This schema contains fields that are common to all note-related schemas.
    """

    title: str = Field(..., min_length=1, max_length=255, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    summary: Optional[str] = Field(None, max_length=500, description="Note summary")
    is_public: bool = Field(default=False, description="Whether the note is public")
    is_pinned: bool = Field(default=False, description="Whether the note is pinned")

    @validator("title")
    def validate_title(cls, v: str) -> str:
        """Validate note title."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @validator("content")
    def validate_content(cls, v: str) -> str:
        """Validate note content."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()

    @validator("summary")
    def validate_summary(cls, v: Optional[str]) -> Optional[str]:
        """Validate note summary."""
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class NoteCreate(NoteBase):
    """
    Schema for note creation.

    This schema is used for creating new notes.
    """

    pass


class NoteUpdate(BaseModel):
    """
    Schema for note updates.

    This schema is used for updating existing notes.
    """

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Note title"
    )
    content: Optional[str] = Field(None, min_length=1, description="Note content")
    summary: Optional[str] = Field(None, max_length=500, description="Note summary")
    is_public: Optional[bool] = Field(None, description="Whether the note is public")
    is_pinned: Optional[bool] = Field(None, description="Whether the note is pinned")

    @validator("title")
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate note title."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else None

    @validator("content")
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate note content."""
        if v is not None and not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip() if v else None

    @validator("summary")
    def validate_summary(cls, v: Optional[str]) -> Optional[str]:
        """Validate note summary."""
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class NoteStatusUpdate(BaseModel):
    """
    Schema for note status updates.

    This schema is used for updating note status (active, archived, deleted).
    """

    status: NoteStatus = Field(..., description="New note status")


class NoteResponse(NoteBase):
    """
    Schema for note responses.

    This schema is used for returning note data in API responses.
    """

    id: int = Field(..., description="Note ID")
    status: NoteStatus = Field(..., description="Note status")
    owner_id: int = Field(..., description="Note owner ID")
    created_at: datetime = Field(..., description="Note creation timestamp")
    updated_at: datetime = Field(..., description="Note last update timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class NoteWithOwner(NoteResponse):
    """
    Schema for notes with owner information.

    This schema includes owner details along with note information.
    """

    owner: dict = Field(..., description="Note owner information")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class NoteListResponse(BaseModel):
    """
    Schema for note list responses.

    This schema is used for returning paginated lists of notes.
    """

    notes: list[NoteResponse] = Field(..., description="List of notes")
    total: int = Field(..., description="Total number of notes")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of notes per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class NoteSearchRequest(BaseModel):
    """
    Schema for note search requests.

    This schema is used for searching notes with various criteria.
    """

    query: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Search query"
    )
    status: Optional[NoteStatus] = Field(None, description="Filter by status")
    is_public: Optional[bool] = Field(None, description="Filter by public status")
    is_pinned: Optional[bool] = Field(None, description="Filter by pinned status")
    created_after: Optional[datetime] = Field(
        None, description="Filter by creation date (after)"
    )
    created_before: Optional[datetime] = Field(
        None, description="Filter by creation date (before)"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(
        default=10, ge=1, le=100, description="Number of notes per page"
    )

    @validator("query")
    def validate_query(cls, v: Optional[str]) -> Optional[str]:
        """Validate search query."""
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class NoteStats(BaseModel):
    """
    Schema for note statistics.

    This schema is used for returning note-related statistics.
    """

    total_notes: int = Field(..., description="Total number of notes")
    active_notes: int = Field(..., description="Number of active notes")
    archived_notes: int = Field(..., description="Number of archived notes")
    public_notes: int = Field(..., description="Number of public notes")
    pinned_notes: int = Field(..., description="Number of pinned notes")
    created_today: int = Field(..., description="Notes created today")
    created_this_week: int = Field(..., description="Notes created this week")
    created_this_month: int = Field(..., description="Notes created this month")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class NoteBulkAction(BaseModel):
    """
    Schema for bulk note actions.

    This schema is used for performing bulk operations on notes.
    """

    note_ids: list[int] = Field(..., min_items=1, description="List of note IDs")
    action: str = Field(..., description="Action to perform")

    @validator("action")
    def validate_action(cls, v: str) -> str:
        """Validate bulk action."""
        allowed_actions = [
            "archive",
            "unarchive",
            "pin",
            "unpin",
            "make_public",
            "make_private",
            "delete",
        ]
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of: {allowed_actions}")
        return v

    @validator("note_ids")
    def validate_note_ids(cls, v: list[int]) -> list[int]:
        """Validate note IDs."""
        if not v:
            raise ValueError("At least one note ID is required")
        if len(set(v)) != len(v):
            raise ValueError("Note IDs must be unique")
        return v
