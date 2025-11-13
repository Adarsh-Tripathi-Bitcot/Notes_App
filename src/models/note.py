"""
Note model for the Notes App.

This module defines the Note database model using SQLAlchemy,
representing notes in the system with full CRUD capabilities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class NoteStatus(str, Enum):
    """Enumeration for note status values."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Note(Base):
    """
    Note model representing a note in the Notes App.

    This model stores note information including content, metadata,
    and relationships to users and other notes.
    """

    __tablename__ = "notes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Note content
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # Note metadata
    status = Column(
        SQLEnum(NoteStatus), default=NoteStatus.ACTIVE, nullable=False, index=True
    )
    is_public = Column(Boolean, default=False, nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)

    # Foreign keys
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="notes", lazy="select")

    def __repr__(self) -> str:
        """String representation of the Note model."""
        return (
            f"<Note(id={self.id}, title='{self.title}', "
            f"status='{self.status}', owner_id={self.owner_id})>"
        )

    @property
    def is_active(self) -> bool:
        """
        Check if the note is active.

        Returns:
            True if the note status is ACTIVE, False otherwise
        """
        return self.status == NoteStatus.ACTIVE

    @property
    def is_archived(self) -> bool:
        """
        Check if the note is archived.

        Returns:
            True if the note status is ARCHIVED, False otherwise
        """
        return self.status == NoteStatus.ARCHIVED

    @property
    def is_deleted(self) -> bool:
        """
        Check if the note is deleted.

        Returns:
            True if the note status is DELETED, False otherwise
        """
        return self.status == NoteStatus.DELETED

    def to_dict(self) -> dict:
        """
        Convert the note model to a dictionary.

        Returns:
            Dictionary representation of the note
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "status": self.status.value if self.status else None,
            "is_public": self.is_public,
            "is_pinned": self.is_pinned,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def activate(self) -> None:
        """Set the note status to active."""
        self.status = NoteStatus.ACTIVE

    def archive(self) -> None:
        """Set the note status to archived."""
        self.status = NoteStatus.ARCHIVED

    def delete(self) -> None:
        """Set the note status to deleted (soft delete)."""
        self.status = NoteStatus.DELETED

    def pin(self) -> None:
        """Pin the note."""
        self.is_pinned = True

    def unpin(self) -> None:
        """Unpin the note."""
        self.is_pinned = False

    def make_public(self) -> None:
        """Make the note public."""
        self.is_public = True

    def make_private(self) -> None:
        """Make the note private."""
        self.is_public = False

    def update_content(
        self, title: str, content: str, summary: Optional[str] = None
    ) -> None:
        """
        Update the note content.

        Args:
            title: New title for the note
            content: New content for the note
            summary: Optional summary for the note
        """
        self.title = title
        self.content = content
        if summary is not None:
            self.summary = summary
        self.updated_at = datetime.utcnow()

    def generate_summary(self, max_length: int = 200) -> str:
        """
        Generate a summary from the note content.

        Args:
            max_length: Maximum length of the summary

        Returns:
            Generated summary
        """
        if not self.content:
            return ""

        # Simple summary generation - take first part of content
        summary = self.content.strip()
        if len(summary) <= max_length:
            return summary

        # Truncate and add ellipsis
        summary = summary[: max_length - 3].strip()
        # Find the last complete word
        last_space = summary.rfind(" ")
        if last_space > max_length // 2:  # Only if we're not cutting too much
            summary = summary[:last_space]

        return summary + "..."

    def auto_generate_summary(self) -> None:
        """Automatically generate and set the summary."""
        self.summary = self.generate_summary()
