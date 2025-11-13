"""
Note repository for data access operations.

This module implements the repository pattern for note-related database operations,
providing a clean abstraction layer between the service layer and data access.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.orm import Session

from ..core.exceptions import DatabaseError
from ..core.logging import get_logger, log_database_operation
from ..core.logging_utils import RepositoryLogger
from ..models.note import Note, NoteStatus

logger = get_logger(__name__)
repo_logger = RepositoryLogger("note_repository")


class NoteRepository:
    """
    Repository class for note-related database operations.

    This class provides methods for CRUD operations on note entities,
    following the repository pattern for clean separation of concerns.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the note repository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, note_data: dict) -> Note:
        """
        Create a new note.

        Args:
            note_data: Dictionary containing note data

        Returns:
            Created note instance

        Raises:
            DatabaseError: If database operation fails
        """
        repo_logger.log_query(
            "INSERT",
            "notes",
            owner_id=note_data.get("owner_id"),
            title=note_data.get("title"),
        )

        with log_database_operation(
            logger, "INSERT", "notes", owner_id=note_data.get("owner_id")
        ):
            try:
                note = Note(**note_data)
                self.db.add(note)
                self.db.commit()
                self.db.refresh(note)

                repo_logger.log_success(
                    "create", note_id=note.id, owner_id=note.owner_id, title=note.title
                )

                logger.info(
                    "Note created successfully", note_id=note.id, owner_id=note.owner_id
                )
                return note

            except Exception as e:
                self.db.rollback()
                repo_logger.log_error(
                    "create",
                    e,
                    owner_id=note_data.get("owner_id"),
                    title=note_data.get("title"),
                )
                logger.error("Failed to create note", error=str(e), note_data=note_data)
                raise DatabaseError(
                    message="Failed to create note",
                    operation="INSERT",
                    details={"error": str(e)},
                )

    def get_by_id(self, note_id: int, owner_id: Optional[int] = None) -> Optional[Note]:
        """
        Get a note by ID.

        Args:
            note_id: Note ID
            owner_id: Optional owner ID for access control

        Returns:
            Note instance if found, None otherwise
        """
        with log_database_operation(
            logger, "SELECT", "notes", note_id=note_id, owner_id=owner_id
        ):
            try:
                query = self.db.query(Note).filter(Note.id == note_id)

                if owner_id is not None:
                    query = query.filter(Note.owner_id == owner_id)

                note = query.first()
                return note

            except Exception as e:
                logger.error(
                    "Failed to get note by ID",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise DatabaseError(
                    message="Failed to get note by ID",
                    operation="SELECT",
                    details={"error": str(e), "note_id": note_id, "owner_id": owner_id},
                )

    def get_by_owner(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[NoteStatus] = None,
        is_public: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        search_query: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> List[Note]:
        """
        Get notes by owner with optional filtering and pagination.

        Args:
            owner_id: Owner ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            is_public: Filter by public status
            is_pinned: Filter by pinned status
            search_query: Search query for title and content
            order_by: Field to order by
            order_direction: Order direction (asc or desc)

        Returns:
            List of note instances
        """
        with log_database_operation(
            logger, "SELECT", "notes", owner_id=owner_id, skip=skip, limit=limit
        ):
            try:
                query = self.db.query(Note).filter(Note.owner_id == owner_id)

                # Apply filters
                if status is not None:
                    query = query.filter(Note.status == status)

                if is_public is not None:
                    query = query.filter(Note.is_public == is_public)

                if is_pinned is not None:
                    query = query.filter(Note.is_pinned == is_pinned)

                if search_query:
                    search_filter = or_(
                        Note.title.ilike(f"%{search_query}%"),
                        Note.content.ilike(f"%{search_query}%"),
                        Note.summary.ilike(f"%{search_query}%"),
                    )
                    query = query.filter(search_filter)

                # Apply ordering
                order_column = getattr(Note, order_by, Note.created_at)
                if order_direction.lower() == "desc":
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))

                # Apply pagination
                notes = query.offset(skip).limit(limit).all()
                return notes

            except Exception as e:
                logger.error(
                    "Failed to get notes by owner", error=str(e), owner_id=owner_id
                )
                raise DatabaseError(
                    message="Failed to get notes by owner",
                    operation="SELECT",
                    details={"error": str(e), "owner_id": owner_id},
                )

    def get_public_notes(
        self,
        skip: int = 0,
        limit: int = 100,
        search_query: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> List[Note]:
        """
        Get public notes with optional filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search_query: Search query for title and content
            order_by: Field to order by
            order_direction: Order direction (asc or desc)

        Returns:
            List of public note instances
        """
        with log_database_operation(
            logger, "SELECT", "notes", skip=skip, limit=limit, is_public=True
        ):
            try:
                query = self.db.query(Note).filter(
                    and_(Note.is_public.is_(True), Note.status == NoteStatus.ACTIVE)
                )

                if search_query:
                    search_filter = or_(
                        Note.title.ilike(f"%{search_query}%"),
                        Note.content.ilike(f"%{search_query}%"),
                        Note.summary.ilike(f"%{search_query}%"),
                    )
                    query = query.filter(search_filter)

                # Apply ordering
                order_column = getattr(Note, order_by, Note.created_at)
                if order_direction.lower() == "desc":
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))

                # Apply pagination
                notes = query.offset(skip).limit(limit).all()
                return notes

            except Exception as e:
                logger.error("Failed to get public notes", error=str(e))
                raise DatabaseError(
                    message="Failed to get public notes",
                    operation="SELECT",
                    details={"error": str(e)},
                )

    def update(
        self, note_id: int, update_data: dict, owner_id: Optional[int] = None
    ) -> Optional[Note]:
        """
        Update a note.

        Args:
            note_id: Note ID
            update_data: Dictionary containing update data
            owner_id: Optional owner ID for access control

        Returns:
            Updated note instance if found, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        with log_database_operation(
            logger, "UPDATE", "notes", note_id=note_id, owner_id=owner_id
        ):
            try:
                note = self.get_by_id(note_id, owner_id)
                if not note:
                    return None

                # Update note fields
                for field, value in update_data.items():
                    if hasattr(note, field):
                        setattr(note, field, value)

                self.db.commit()
                self.db.refresh(note)

                logger.info(
                    "Note updated successfully", note_id=note_id, owner_id=owner_id
                )
                return note

            except Exception as e:
                self.db.rollback()
                logger.error(
                    "Failed to update note",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise DatabaseError(
                    message="Failed to update note",
                    operation="UPDATE",
                    details={"error": str(e), "note_id": note_id, "owner_id": owner_id},
                )

    def delete(self, note_id: int, owner_id: Optional[int] = None) -> bool:
        """
        Delete a note (soft delete by default).

        Args:
            note_id: Note ID
            owner_id: Optional owner ID for access control

        Returns:
            True if note was deleted, False if not found
        """
        with log_database_operation(
            logger, "DELETE", "notes", note_id=note_id, owner_id=owner_id
        ):
            try:
                note = self.get_by_id(note_id, owner_id)
                if not note:
                    return False

                # Soft delete by setting status to DELETED
                note.status = NoteStatus.DELETED
                self.db.commit()

                logger.info(
                    "Note deleted successfully", note_id=note_id, owner_id=owner_id
                )
                return True

            except Exception as e:
                self.db.rollback()
                logger.error(
                    "Failed to delete note",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise DatabaseError(
                    message="Failed to delete note",
                    operation="DELETE",
                    details={"error": str(e), "note_id": note_id, "owner_id": owner_id},
                )

    def hard_delete(self, note_id: int, owner_id: Optional[int] = None) -> bool:
        """
        Permanently delete a note from the database.

        Args:
            note_id: Note ID
            owner_id: Optional owner ID for access control

        Returns:
            True if note was deleted, False if not found
        """
        with log_database_operation(
            logger,
            "DELETE",
            "notes",
            note_id=note_id,
            owner_id=owner_id,
            hard_delete=True,
        ):
            try:
                note = self.get_by_id(note_id, owner_id)
                if not note:
                    return False

                self.db.delete(note)
                self.db.commit()

                logger.info(
                    "Note permanently deleted", note_id=note_id, owner_id=owner_id
                )
                return True

            except Exception as e:
                self.db.rollback()
                logger.error(
                    "Failed to permanently delete note",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise DatabaseError(
                    message="Failed to permanently delete note",
                    operation="DELETE",
                    details={"error": str(e), "note_id": note_id, "owner_id": owner_id},
                )

    def count_by_owner(
        self,
        owner_id: int,
        status: Optional[NoteStatus] = None,
        is_public: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        search_query: Optional[str] = None,
    ) -> int:
        """
        Count notes by owner with optional filtering.

        Args:
            owner_id: Owner ID
            status: Filter by status
            is_public: Filter by public status
            is_pinned: Filter by pinned status
            search_query: Search query for title and content

        Returns:
            Number of notes matching the criteria
        """
        with log_database_operation(logger, "SELECT", "notes", owner_id=owner_id):
            try:
                query = self.db.query(Note).filter(Note.owner_id == owner_id)

                if status is not None:
                    query = query.filter(Note.status == status)

                if is_public is not None:
                    query = query.filter(Note.is_public == is_public)

                if is_pinned is not None:
                    query = query.filter(Note.is_pinned == is_pinned)

                if search_query:
                    search_filter = or_(
                        Note.title.ilike(f"%{search_query}%"),
                        Note.content.ilike(f"%{search_query}%"),
                        Note.summary.ilike(f"%{search_query}%"),
                    )
                    query = query.filter(search_filter)

                count = query.count()
                return count

            except Exception as e:
                logger.error(
                    "Failed to count notes by owner", error=str(e), owner_id=owner_id
                )
                raise DatabaseError(
                    message="Failed to count notes by owner",
                    operation="SELECT",
                    details={"error": str(e), "owner_id": owner_id},
                )

    def count_public_notes(self, search_query: Optional[str] = None) -> int:
        """
        Count public notes with optional filtering.

        Args:
            search_query: Search query for title and content

        Returns:
            Number of public notes matching the criteria
        """
        with log_database_operation(logger, "COUNT", "notes", is_public=True):
            try:
                query = self.db.query(Note).filter(
                    and_(Note.is_public.is_(True), Note.status == NoteStatus.ACTIVE)
                )

                if search_query:
                    search_filter = or_(
                        Note.title.ilike(f"%{search_query}%"),
                        Note.content.ilike(f"%{search_query}%"),
                        Note.summary.ilike(f"%{search_query}%"),
                    )
                    query = query.filter(search_filter)

                count = query.count()
                return count

            except Exception as e:
                logger.error("Failed to count public notes", error=str(e))
                raise DatabaseError(
                    message="Failed to count public notes",
                    operation="SELECT",
                    details={"error": str(e)},
                )

    def get_stats(self, owner_id: int) -> dict:
        """
        Get note statistics for an owner.

        Args:
            owner_id: Owner ID

        Returns:
            Dictionary containing note statistics
        """
        with log_database_operation(logger, "SELECT", "notes", owner_id=owner_id):
            try:
                # Total notes
                total_notes = (
                    self.db.query(Note).filter(Note.owner_id == owner_id).count()
                )

                # Active notes
                active_notes = (
                    self.db.query(Note)
                    .filter(
                        and_(
                            Note.owner_id == owner_id, Note.status == NoteStatus.ACTIVE
                        )
                    )
                    .count()
                )

                # Archived notes
                archived_notes = (
                    self.db.query(Note)
                    .filter(
                        and_(
                            Note.owner_id == owner_id,
                            Note.status == NoteStatus.ARCHIVED,
                        )
                    )
                    .count()
                )

                # Public notes
                public_notes = (
                    self.db.query(Note)
                    .filter(and_(Note.owner_id == owner_id, Note.is_public.is_(True)))
                    .count()
                )

                # Pinned notes
                pinned_notes = (
                    self.db.query(Note)
                    .filter(and_(Note.owner_id == owner_id, Note.is_pinned.is_(True)))
                    .count()
                )

                # Notes created today
                today = datetime.utcnow().date()
                created_today = (
                    self.db.query(Note)
                    .filter(
                        and_(
                            Note.owner_id == owner_id,
                            func.date(Note.created_at) == today,
                        )
                    )
                    .count()
                )

                # Notes created this week
                week_start = today - timedelta(days=today.weekday())
                created_this_week = (
                    self.db.query(Note)
                    .filter(
                        and_(
                            Note.owner_id == owner_id,
                            func.date(Note.created_at) >= week_start,
                        )
                    )
                    .count()
                )

                # Notes created this month
                month_start = today.replace(day=1)
                created_this_month = (
                    self.db.query(Note)
                    .filter(
                        and_(
                            Note.owner_id == owner_id,
                            func.date(Note.created_at) >= month_start,
                        )
                    )
                    .count()
                )

                return {
                    "total_notes": total_notes,
                    "active_notes": active_notes,
                    "archived_notes": archived_notes,
                    "public_notes": public_notes,
                    "pinned_notes": pinned_notes,
                    "created_today": created_today,
                    "created_this_week": created_this_week,
                    "created_this_month": created_this_month,
                }

            except Exception as e:
                logger.error(
                    "Failed to get note stats", error=str(e), owner_id=owner_id
                )
                raise DatabaseError(
                    message="Failed to get note stats",
                    operation="SELECT",
                    details={"error": str(e), "owner_id": owner_id},
                )

    def bulk_update_status(
        self, note_ids: List[int], status: NoteStatus, owner_id: Optional[int] = None
    ) -> int:
        """
        Bulk update note status.

        Args:
            note_ids: List of note IDs
            status: New status
            owner_id: Optional owner ID for access control

        Returns:
            Number of notes updated
        """
        with log_database_operation(
            logger,
            "UPDATE",
            "notes",
            note_ids=note_ids,
            status=status,
            owner_id=owner_id,
        ):
            try:
                query = self.db.query(Note).filter(Note.id.in_(note_ids))

                if owner_id is not None:
                    query = query.filter(Note.owner_id == owner_id)

                updated_count = query.update(
                    {"status": status}, synchronize_session=False
                )

                self.db.commit()

                logger.info(
                    "Bulk status update completed",
                    updated_count=updated_count,
                    status=status,
                )
                return updated_count

            except Exception as e:
                self.db.rollback()
                logger.error(
                    "Failed to bulk update note status", error=str(e), note_ids=note_ids
                )
                raise DatabaseError(
                    message="Failed to bulk update note status",
                    operation="UPDATE",
                    details={"error": str(e), "note_ids": note_ids},
                )

    def exists(self, note_id: int, owner_id: Optional[int] = None) -> bool:
        """
        Check if a note exists.

        Args:
            note_id: Note ID
            owner_id: Optional owner ID for access control

        Returns:
            True if note exists, False otherwise
        """
        with log_database_operation(
            logger,
            "EXISTS",
            "notes",
            note_id=note_id,
            owner_id=owner_id,
        ):
            try:
                query = self.db.query(Note).filter(Note.id == note_id)

                if owner_id is not None:
                    query = query.filter(Note.owner_id == owner_id)

                exists = query.first() is not None
                return exists

            except Exception as e:
                logger.error(
                    "Failed to check if note exists",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise DatabaseError(
                    message="Failed to check if note exists",
                    operation="SELECT",
                    details={"error": str(e), "note_id": note_id, "owner_id": owner_id},
                )
