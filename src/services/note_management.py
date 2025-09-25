"""
Note management service for note operations.

This module provides business logic for note management including
CRUD operations, search, filtering, and note statistics.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from ..core.exceptions import AuthorizationError, NotFoundError, ValidationError
from ..core.logging import get_logger, log_function_call
from ..models.note import Note, NoteStatus
from ..repositories.note_repository import NoteRepository
from ..schemas.note import (
    NoteBulkAction,
    NoteCreate,
    NoteListResponse,
    NoteResponse,
    NoteSearchRequest,
    NoteStats,
    NoteStatusUpdate,
    NoteUpdate,
)

logger = get_logger(__name__)


class NoteManagementService:
    """
    Service class for note management operations.

    This class handles business logic for note operations including
    CRUD operations, search, filtering, and statistics.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the note management service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.note_repository = NoteRepository(db)

    def create_note(self, note_data: NoteCreate, owner_id: int) -> Note:
        """
        Create a new note.

        Args:
            note_data: Note creation data
            owner_id: Owner user ID

        Returns:
            Created note instance

        Raises:
            ValidationError: If validation fails
        """
        with log_function_call(
            logger, "create_note", owner_id=owner_id, title=note_data.title
        ):
            try:
                # Prepare note data
                note_dict = {
                    "title": note_data.title,
                    "content": note_data.content,
                    "summary": note_data.summary,
                    "is_public": note_data.is_public,
                    "is_pinned": note_data.is_pinned,
                    "owner_id": owner_id,
                    "status": NoteStatus.ACTIVE,
                }

                # Auto-generate summary if not provided
                if not note_dict["summary"]:
                    note = Note(**note_dict)
                    note_dict["summary"] = note.generate_summary()

                # Create note
                note = self.note_repository.create(note_dict)

                logger.info(
                    "Note created successfully", note_id=note.id, owner_id=owner_id
                )
                return note

            except Exception as e:
                logger.error("Failed to create note", error=str(e), owner_id=owner_id)
                raise ValidationError(
                    message="Failed to create note", details={"error": str(e)}
                )

    def get_note(self, note_id: int, owner_id: int) -> Optional[Note]:
        """
        Get a note by ID.

        Args:
            note_id: Note ID
            owner_id: Owner user ID

        Returns:
            Note instance if found, None otherwise
        """
        with log_function_call(logger, "get_note", note_id=note_id, owner_id=owner_id):
            try:
                note = self.note_repository.get_by_id(note_id, owner_id)
                return note
            except Exception as e:
                logger.error(
                    "Failed to get note",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise ValidationError(
                    message="Failed to get note", details={"error": str(e)}
                )

    def get_notes(
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
        Get notes for a user with optional filtering and pagination.

        Args:
            owner_id: Owner user ID
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
        with log_function_call(
            logger, "get_notes", owner_id=owner_id, skip=skip, limit=limit
        ):
            try:
                notes = self.note_repository.get_by_owner(
                    owner_id=owner_id,
                    skip=skip,
                    limit=limit,
                    status=status,
                    is_public=is_public,
                    is_pinned=is_pinned,
                    search_query=search_query,
                    order_by=order_by,
                    order_direction=order_direction,
                )
                return notes
            except Exception as e:
                logger.error("Failed to get notes", error=str(e), owner_id=owner_id)
                raise ValidationError(
                    message="Failed to get notes", details={"error": str(e)}
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
        with log_function_call(logger, "get_public_notes", skip=skip, limit=limit):
            try:
                notes = self.note_repository.get_public_notes(
                    skip=skip,
                    limit=limit,
                    search_query=search_query,
                    order_by=order_by,
                    order_direction=order_direction,
                )
                return notes
            except Exception as e:
                logger.error("Failed to get public notes", error=str(e))
                raise ValidationError(
                    message="Failed to get public notes", details={"error": str(e)}
                )

    def update_note(
        self, note_id: int, note_data: NoteUpdate, owner_id: int
    ) -> Optional[Note]:
        """
        Update a note.

        Args:
            note_id: Note ID
            note_data: Note update data
            owner_id: Owner user ID

        Returns:
            Updated note instance if found, None otherwise

        Raises:
            NotFoundError: If note not found
            AuthorizationError: If user not authorized
        """
        with log_function_call(
            logger, "update_note", note_id=note_id, owner_id=owner_id
        ):
            try:
                # Check if note exists and user owns it
                note = self.note_repository.get_by_id(note_id, owner_id)
                if not note:
                    raise NotFoundError("Note", str(note_id))

                # Prepare update data
                update_data = {}
                for field, value in note_data.dict(exclude_unset=True).items():
                    if value is not None:
                        update_data[field] = value

                # Auto-generate summary if content is updated
                # and summary is not provided
                if "content" in update_data and "summary" not in update_data:
                    note.content = update_data["content"]
                    update_data["summary"] = note.generate_summary()

                # Update note
                updated_note = self.note_repository.update(
                    note_id, update_data, owner_id
                )

                logger.info(
                    "Note updated successfully", note_id=note_id, owner_id=owner_id
                )
                return updated_note

            except (NotFoundError, AuthorizationError):
                raise
            except Exception as e:
                logger.error(
                    "Failed to update note",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise ValidationError(
                    message="Failed to update note", details={"error": str(e)}
                )

    def delete_note(self, note_id: int, owner_id: int) -> bool:
        """
        Delete a note (soft delete).

        Args:
            note_id: Note ID
            owner_id: Owner user ID

        Returns:
            True if note deleted successfully, False otherwise

        Raises:
            NotFoundError: If note not found
            AuthorizationError: If user not authorized
        """
        with log_function_call(
            logger, "delete_note", note_id=note_id, owner_id=owner_id
        ):
            try:
                # Check if note exists and user owns it
                note = self.note_repository.get_by_id(note_id, owner_id)
                if not note:
                    raise NotFoundError("Note", str(note_id))

                # Delete note
                deleted = self.note_repository.delete(note_id, owner_id)

                if deleted:
                    logger.info(
                        "Note deleted successfully", note_id=note_id, owner_id=owner_id
                    )
                else:
                    logger.warning(
                        "Note deletion failed", note_id=note_id, owner_id=owner_id
                    )

                return deleted

            except (NotFoundError, AuthorizationError):
                raise
            except Exception as e:
                logger.error(
                    "Failed to delete note",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise ValidationError(
                    message="Failed to delete note", details={"error": str(e)}
                )

    def update_note_status(
        self, note_id: int, status_data: NoteStatusUpdate, owner_id: int
    ) -> Optional[Note]:
        """
        Update note status.

        Args:
            note_id: Note ID
            status_data: Status update data
            owner_id: Owner user ID

        Returns:
            Updated note instance if found, None otherwise

        Raises:
            NotFoundError: If note not found
            AuthorizationError: If user not authorized
        """
        with log_function_call(
            logger,
            "update_note_status",
            note_id=note_id,
            owner_id=owner_id,
            status=status_data.status,
        ):
            try:
                # Check if note exists and user owns it
                note = self.note_repository.get_by_id(note_id, owner_id)
                if not note:
                    raise NotFoundError("Note", str(note_id))

                # Update status
                update_data = {"status": status_data.status}
                updated_note = self.note_repository.update(
                    note_id, update_data, owner_id
                )

                logger.info(
                    "Note status updated successfully",
                    note_id=note_id,
                    owner_id=owner_id,
                    status=status_data.status,
                )
                return updated_note

            except (NotFoundError, AuthorizationError):
                raise
            except Exception as e:
                logger.error(
                    "Failed to update note status",
                    error=str(e),
                    note_id=note_id,
                    owner_id=owner_id,
                )
                raise ValidationError(
                    message="Failed to update note status", details={"error": str(e)}
                )

    def search_notes(
        self, search_request: NoteSearchRequest, owner_id: int
    ) -> Tuple[List[NoteResponse], int]:
        """
        Search notes with various criteria.

        Args:
            search_request: Search criteria
            owner_id: Owner user ID

        Returns:
            Tuple of (note responses list, total count)
        """
        with log_function_call(
            logger, "search_notes", owner_id=owner_id, query=search_request.query
        ):
            try:
                # Get notes with search criteria
                notes = self.note_repository.get_by_owner(
                    owner_id=owner_id,
                    skip=(search_request.page - 1) * search_request.per_page,
                    limit=search_request.per_page,
                    status=search_request.status,
                    is_public=search_request.is_public,
                    is_pinned=search_request.is_pinned,
                    search_query=search_request.query,
                    order_by="created_at",
                    order_direction="desc",
                )

                # Get total count
                total = self.note_repository.count_by_owner(
                    owner_id=owner_id,
                    status=search_request.status,
                    is_public=search_request.is_public,
                    is_pinned=search_request.is_pinned,
                    search_query=search_request.query,
                )

                # Convert Note objects to NoteResponse objects
                note_responses = [NoteResponse.from_orm(note) for note in notes]

                return note_responses, total

            except Exception as e:
                logger.error("Failed to search notes", error=str(e), owner_id=owner_id)
                raise ValidationError(
                    message="Failed to search notes", details={"error": str(e)}
                )

    def get_note_stats(self, owner_id: int) -> NoteStats:
        """
        Get note statistics for a user.

        Args:
            owner_id: Owner user ID

        Returns:
            Note statistics

        Raises:
            ValidationError: If operation fails
        """
        with log_function_call(logger, "get_note_stats", owner_id=owner_id):
            try:
                stats = self.note_repository.get_stats(owner_id)

                # Calculate additional stats
                today = datetime.utcnow().date()
                week_start = today - timedelta(days=today.weekday())
                month_start = today.replace(day=1)

                # Get notes created this week
                week_notes = self.note_repository.get_by_owner(
                    owner_id=owner_id,
                    skip=0,
                    limit=1000,  # Large limit to get all notes
                    order_by="created_at",
                    order_direction="desc",
                )

                created_this_week = sum(
                    1 for note in week_notes if note.created_at.date() >= week_start
                )
                created_this_month = sum(
                    1 for note in week_notes if note.created_at.date() >= month_start
                )

                return NoteStats(
                    total_notes=stats["total_notes"],
                    active_notes=stats["active_notes"],
                    archived_notes=stats["archived_notes"],
                    public_notes=stats["public_notes"],
                    pinned_notes=stats["pinned_notes"],
                    created_today=stats["created_today"],
                    created_this_week=created_this_week,
                    created_this_month=created_this_month,
                )

            except Exception as e:
                logger.error(
                    "Failed to get note stats", error=str(e), owner_id=owner_id
                )
                raise ValidationError(
                    message="Failed to get note stats", details={"error": str(e)}
                )

    def bulk_action(self, bulk_action: NoteBulkAction, owner_id: int) -> int:
        """
        Perform bulk action on notes.

        Args:
            bulk_action: Bulk action data
            owner_id: Owner user ID

        Returns:
            Number of notes affected

        Raises:
            ValidationError: If operation fails
        """
        with log_function_call(
            logger,
            "bulk_action",
            owner_id=owner_id,
            action=bulk_action.action,
            note_count=len(bulk_action.note_ids),
        ):
            try:
                # Verify all notes exist and belong to user
                for note_id in bulk_action.note_ids:
                    note = self.note_repository.get_by_id(note_id, owner_id)
                    if not note:
                        raise NotFoundError("Note", str(note_id))

                # Perform bulk action
                if bulk_action.action in ["archive", "unarchive"]:
                    status = (
                        NoteStatus.ARCHIVED
                        if bulk_action.action == "archive"
                        else NoteStatus.ACTIVE
                    )
                    updated_count = self.note_repository.bulk_update_status(
                        bulk_action.note_ids, status, owner_id
                    )
                elif bulk_action.action in ["pin", "unpin"]:
                    is_pinned = bulk_action.action == "pin"
                    update_data = {"is_pinned": is_pinned}
                    updated_count = 0
                    for note_id in bulk_action.note_ids:
                        if self.note_repository.update(note_id, update_data, owner_id):
                            updated_count += 1
                elif bulk_action.action in ["make_public", "make_private"]:
                    is_public = bulk_action.action == "make_public"
                    update_data = {"is_public": is_public}
                    updated_count = 0
                    for note_id in bulk_action.note_ids:
                        if self.note_repository.update(note_id, update_data, owner_id):
                            updated_count += 1
                elif bulk_action.action == "delete":
                    updated_count = 0
                    for note_id in bulk_action.note_ids:
                        if self.note_repository.delete(note_id, owner_id):
                            updated_count += 1
                else:
                    raise ValidationError(
                        message="Invalid bulk action",
                        details={"action": bulk_action.action},
                    )

                logger.info(
                    "Bulk action completed",
                    action=bulk_action.action,
                    updated_count=updated_count,
                    owner_id=owner_id,
                )
                return updated_count

            except (NotFoundError, ValidationError):
                raise
            except Exception as e:
                logger.error(
                    "Failed to perform bulk action", error=str(e), owner_id=owner_id
                )
                raise ValidationError(
                    message="Failed to perform bulk action", details={"error": str(e)}
                )

    def get_paginated_notes(
        self,
        owner_id: int,
        page: int = 1,
        per_page: int = 10,
        status: Optional[NoteStatus] = None,
        search_query: Optional[str] = None,
    ) -> NoteListResponse:
        """
        Get paginated notes for a user.

        Args:
            owner_id: Owner user ID
            page: Page number
            per_page: Number of notes per page
            status: Filter by status
            search_query: Search query

        Returns:
            Paginated note list response
        """
        with log_function_call(
            logger,
            "get_paginated_notes",
            owner_id=owner_id,
            page=page,
            per_page=per_page,
        ):
            try:
                skip = (page - 1) * per_page

                # Get notes
                notes = self.note_repository.get_by_owner(
                    owner_id=owner_id,
                    skip=skip,
                    limit=per_page,
                    status=status,
                    search_query=search_query,
                    order_by="created_at",
                    order_direction="desc",
                )

                # Get total count
                total = self.note_repository.count_by_owner(
                    owner_id=owner_id, status=status, search_query=search_query
                )

                # Calculate total pages
                total_pages = (total + per_page - 1) // per_page

                # Convert Note objects to NoteResponse objects
                note_responses = [NoteResponse.from_orm(note) for note in notes]

                return NoteListResponse(
                    notes=note_responses,
                    total=total,
                    page=page,
                    per_page=per_page,
                    total_pages=total_pages,
                )

            except Exception as e:
                logger.error(
                    "Failed to get paginated notes", error=str(e), owner_id=owner_id
                )
                raise ValidationError(
                    message="Failed to get paginated notes", details={"error": str(e)}
                )
