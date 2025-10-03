"""
Notes router for note-related API endpoints.

This module defines all note-related API endpoints including
CRUD operations, search, filtering, and note management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.exceptions import AuthorizationError, NotFoundError, ValidationError
from ...core.logging import get_logger, log_api_request
from ...core.logging_utils import APILogger
from ...models.note import NoteStatus
from ...schemas.note import (
    NoteBulkAction,
    NoteCreate,
    NoteListResponse,
    NoteResponse,
    NoteSearchRequest,
    NoteStats,
    NoteStatusUpdate,
    NoteUpdate,
)
from ...services.authentication import AuthenticationService
from ...services.note_management import NoteManagementService

logger = get_logger(__name__)
api_logger = APILogger("notes")

# Create router
router = APIRouter()

# HTTP Bearer scheme for JWT token authentication
bearer_scheme = HTTPBearer()


def get_note_service(db: Session = Depends(get_db)) -> NoteManagementService:
    """
    Get note management service dependency.

    Args:
        db: Database session

    Returns:
        Note management service instance
    """
    return NoteManagementService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    """
    Get authentication service dependency.

    Args:
        db: Database session

    Returns:
        Authentication service instance
    """
    return AuthenticationService(db)


# Dependency for getting current user
async def get_current_user_dependency(
    token=Depends(bearer_scheme),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Get current authenticated user from JWT token.

    Args:
        token: HTTPBearer token object containing credentials
        auth_service: Authentication service

    Returns:
        Current user information

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Extract the token string from HTTPBearer
        token_string = token.credentials
        user = auth_service.get_current_user(token_string)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Create a new note.

    Args:
        note_data: Note creation data
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Created note information

    Raises:
        HTTPException: If note creation fails
    """
    api_logger.log_request(
        "POST",
        "/",
        user_id=current_user.id,
        title=note_data.title,
        is_public=note_data.is_public,
    )

    with log_api_request(logger, "POST", "/", user_id=current_user.id):
        try:
            note = note_service.create_note(note_data, current_user.id)

            api_logger.log_response(
                "POST", "/", 201, note_id=note.id, user_id=current_user.id
            )

            logger.info(
                "Note created successfully", note_id=note.id, user_id=current_user.id
            )
            return note
        except ValidationError as e:
            api_logger.log_error(
                "POST", "/", e, user_id=current_user.id, title=note_data.title
            )
            logger.warning(
                "Note creation failed: validation error",
                error=e.message,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            api_logger.log_error(
                "POST", "/", e, user_id=current_user.id, title=note_data.title
            )
            logger.error("Note creation failed", error=str(e), user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create note",
            )


@router.get("/", response_model=NoteListResponse)
async def get_notes(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Number of notes per page"),
    status: Optional[NoteStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search query"),
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Get notes for the current user with pagination and filtering.

    Args:
        page: Page number
        per_page: Number of notes per page
        status: Filter by status
        search: Search query
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Paginated list of notes

    Raises:
        HTTPException: If retrieval fails
    """
    with log_api_request(logger, "GET", "/", user_id=current_user.id):
        try:
            notes_response = note_service.get_paginated_notes(
                owner_id=current_user.id,
                page=page,
                per_page=per_page,
                status=status,
                search_query=search,
            )
            logger.info(
                "Notes retrieved successfully",
                user_id=current_user.id,
                count=len(notes_response.notes),
            )
            return notes_response
        except ValidationError as e:
            logger.warning(
                "Notes retrieval failed: validation error",
                error=e.message,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            logger.error(
                "Notes retrieval failed", error=str(e), user_id=current_user.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve notes",
            )


@router.get("/public", response_model=List[NoteResponse])
async def get_public_notes(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Number of notes per page"),
    search: Optional[str] = Query(None, description="Search query"),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Get public notes with pagination and search.

    Args:
        page: Page number
        per_page: Number of notes per page
        search: Search query
        note_service: Note management service

    Returns:
        List of public notes

    Raises:
        HTTPException: If retrieval fails
    """
    with log_api_request(logger, "GET", "/public"):
        try:
            skip = (page - 1) * per_page
            notes = note_service.get_public_notes(
                skip=skip, limit=per_page, search_query=search
            )
            logger.info("Public notes retrieved successfully", count=len(notes))
            return notes
        except ValidationError as e:
            logger.warning(
                "Public notes retrieval failed: validation error", error=e.message
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            logger.error("Public notes retrieval failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve public notes",
            )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Get a specific note by ID.

    Args:
        note_id: Note ID
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Note information

    Raises:
        HTTPException: If note not found or access denied
    """
    with log_api_request(
        logger, "GET", f"/{note_id}", user_id=current_user.id, note_id=note_id
    ):
        try:
            note = note_service.get_note(note_id, current_user.id)
            if not note:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
                )
            logger.info(
                "Note retrieved successfully", note_id=note_id, user_id=current_user.id
            )
            return note
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Note retrieval failed",
                error=str(e),
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve note",
            )


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Update a specific note.

    Args:
        note_id: Note ID
        note_data: Note update data
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Updated note information

    Raises:
        HTTPException: If update fails
    """
    with log_api_request(
        logger, "PUT", f"/{note_id}", user_id=current_user.id, note_id=note_id
    ):
        try:
            updated_note = note_service.update_note(note_id, note_data, current_user.id)
            if not updated_note:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
                )
            logger.info(
                "Note updated successfully", note_id=note_id, user_id=current_user.id
            )
            return updated_note
        except (NotFoundError, AuthorizationError) as e:
            logger.warning(
                "Note update failed: not found or unauthorized",
                error=e.message,
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except ValidationError as e:
            logger.warning(
                "Note update failed: validation error",
                error=e.message,
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Note update failed",
                error=str(e),
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update note",
            )


@router.put("/{note_id}/status", response_model=NoteResponse)
async def update_note_status(
    note_id: int,
    status_data: NoteStatusUpdate,
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Update note status (active, archived, deleted).

    Args:
        note_id: Note ID
        status_data: Status update data
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Updated note information

    Raises:
        HTTPException: If update fails
    """
    with log_api_request(
        logger,
        "PUT",
        f"/{note_id}/status",
        user_id=current_user.id,
        note_id=note_id,
        status=status_data.status,
    ):
        try:
            updated_note = note_service.update_note_status(
                note_id, status_data, current_user.id
            )
            if not updated_note:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
                )
            logger.info(
                "Note status updated successfully",
                note_id=note_id,
                user_id=current_user.id,
                status=status_data.status,
            )
            return updated_note
        except (NotFoundError, AuthorizationError) as e:
            logger.warning(
                "Note status update failed: not found or unauthorized",
                error=e.message,
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except ValidationError as e:
            logger.warning(
                "Note status update failed: validation error",
                error=e.message,
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Note status update failed",
                error=str(e),
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update note status",
            )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Delete a specific note (soft delete).

    Args:
        note_id: Note ID
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        No content on success

    Raises:
        HTTPException: If deletion fails
    """
    with log_api_request(
        logger, "DELETE", f"/{note_id}", user_id=current_user.id, note_id=note_id
    ):
        try:
            deleted = note_service.delete_note(note_id, current_user.id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
                )
            logger.info(
                "Note deleted successfully", note_id=note_id, user_id=current_user.id
            )
        except (NotFoundError, AuthorizationError) as e:
            logger.warning(
                "Note deletion failed: not found or unauthorized",
                error=e.message,
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Note deletion failed",
                error=str(e),
                note_id=note_id,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete note",
            )


@router.post("/search", response_model=NoteListResponse)
async def search_notes(
    search_request: NoteSearchRequest,
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Search notes with various criteria.

    Args:
        search_request: Search criteria
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Search results with pagination

    Raises:
        HTTPException: If search fails
    """
    with log_api_request(
        logger, "POST", "/search", user_id=current_user.id, query=search_request.query
    ):
        try:
            notes, total = note_service.search_notes(search_request, current_user.id)

            # Calculate total pages
            total_pages = (
                total + search_request.per_page - 1
            ) // search_request.per_page

            response = NoteListResponse(
                notes=notes,
                total=total,
                page=search_request.page,
                per_page=search_request.per_page,
                total_pages=total_pages,
            )

            logger.info(
                "Notes search completed successfully",
                user_id=current_user.id,
                total=total,
            )
            return response
        except ValidationError as e:
            logger.warning(
                "Notes search failed: validation error",
                error=e.message,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            logger.error("Notes search failed", error=str(e), user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search notes",
            )


@router.get("/stats/overview", response_model=NoteStats)
async def get_note_stats(
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Get note statistics for the current user.

    Args:
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Note statistics

    Raises:
        HTTPException: If retrieval fails
    """
    with log_api_request(logger, "GET", "/stats/overview", user_id=current_user.id):
        try:
            stats = note_service.get_note_stats(current_user.id)
            logger.info("Note stats retrieved successfully", user_id=current_user.id)
            return stats
        except ValidationError as e:
            logger.warning(
                "Note stats retrieval failed: validation error",
                error=e.message,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            logger.error(
                "Note stats retrieval failed", error=str(e), user_id=current_user.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve note statistics",
            )


@router.post("/bulk-action", status_code=status.HTTP_200_OK)
async def bulk_action(
    bulk_action: NoteBulkAction,
    current_user=Depends(get_current_user_dependency),
    note_service: NoteManagementService = Depends(get_note_service),
):
    """
    Perform bulk action on multiple notes.

    Args:
        bulk_action: Bulk action data
        current_user: Current authenticated user
        note_service: Note management service

    Returns:
        Number of notes affected

    Raises:
        HTTPException: If bulk action fails
    """
    with log_api_request(
        logger,
        "POST",
        "/bulk-action",
        user_id=current_user.id,
        action=bulk_action.action,
        note_count=len(bulk_action.note_ids),
    ):
        try:
            affected_count = note_service.bulk_action(bulk_action, current_user.id)
            logger.info(
                "Bulk action completed successfully",
                user_id=current_user.id,
                action=bulk_action.action,
                affected_count=affected_count,
            )
            return {
                "message": "Bulk action completed successfully",
                "affected_count": affected_count,
            }
        except (NotFoundError, ValidationError) as e:
            logger.warning(
                "Bulk action failed: validation error",
                error=e.message,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            logger.error("Bulk action failed", error=str(e), user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to perform bulk action",
            )
