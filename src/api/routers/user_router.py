"""
User router for user-related API endpoints.

This module defines all user-related API endpoints including
registration, login, profile management, and authentication.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ...core.auth_bypass import AuthBypass
from ...core.config import settings
from ...core.database import get_db
from ...core.exceptions import AuthenticationError, NotFoundError, ValidationError
from ...core.logging import get_logger, log_api_request
from ...schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserPasswordUpdate,
    UserProfile,
    UserResponse,
    UserStats,
    UserUpdate,
)
from ...services.authentication import AuthenticationService

logger = get_logger(__name__)

# Create router
router = APIRouter()

# HTTP Bearer scheme for JWT token authentication
bearer_scheme = HTTPBearer(auto_error=False)


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
    db: Session = Depends(get_db),
) -> UserResponse:
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
        # Authentication bypass without Authorization header
        if AuthBypass.is_bypass_enabled():
            # Attempt to find or create a test user based on env credentials
            test_email = settings.test_user_email
            user = auth_service.user_repository.get_by_email(test_email)
            if not user:
                # Create a test user if not present
                hashed_password = auth_service.get_password_hash("test-password")
                user_dict = {
                    "email": test_email,
                    "username": settings.test_user_username,
                    "first_name": settings.test_user_full_name.split(" ")[0]
                    if settings.test_user_full_name
                    else "Test",
                    "last_name": "",
                    "bio": "Test bypass user",
                    "hashed_password": hashed_password,
                    "is_active": True,
                    "is_verified": True,
                }
                user = auth_service.user_repository.create(user_dict)
            return user

        # Extract the token string from HTTPBearer
        token_string = token.credentials if token else None
        user = auth_service.get_current_user(token_string)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        auth_service: Authentication service

    Returns:
        Created user information

    Raises:
        HTTPException: If registration fails
    """
    with log_api_request(logger, "POST", "/register"):
        try:
            user = auth_service.register_user(user_data)
            logger.info(
                "User registered successfully", user_id=user.id, email=user.email
            )
            return user
        except ValidationError as e:
            logger.warning(
                "User registration failed: validation error",
                error=e.message,
                details=e.details,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            logger.error("User registration failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed",
            )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Login a user and return access token.

    Args:
        login_data: User login data
        auth_service: Authentication service

    Returns:
        Access token and metadata

    Raises:
        HTTPException: If login fails
    """
    with log_api_request(logger, "POST", "/login", user_email=login_data.email):
        try:
            token_response = auth_service.login_user(login_data)
            logger.info("User logged in successfully", email=login_data.email)
            return token_response
        except AuthenticationError as e:
            logger.warning(
                "User login failed: authentication error",
                error=e.message,
                email=login_data.email,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message
            )
        except Exception as e:
            logger.error("User login failed", error=str(e), email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
            )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user_dependency),
):
    """
    Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user profile information
    """
    with log_api_request(logger, "GET", "/me", user_id=current_user.id):
        try:
            logger.info("User profile retrieved successfully", user_id=current_user.id)
            return current_user
        except Exception as e:
            logger.error(
                "Failed to get user profile", error=str(e), user_id=current_user.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user profile",
            )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Update current user profile.

    Args:
        user_data: User update data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Updated user information

    Raises:
        HTTPException: If update fails
    """
    with log_api_request(logger, "PUT", "/me", user_id=current_user.id):
        try:
            # Convert UserResponse to dict for update
            update_data = user_data.dict(exclude_unset=True)

            # Update user
            updated_user = auth_service.user_repository.update(
                current_user.id, update_data
            )
            if not updated_user:
                raise NotFoundError("User", str(current_user.id))

            logger.info("User profile updated successfully", user_id=current_user.id)
            return updated_user
        except NotFoundError as e:
            logger.warning("User not found for update", user_id=current_user.id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except ValidationError as e:
            logger.warning(
                "User update failed: validation error",
                error=e.message,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        except Exception as e:
            logger.error("User update failed", error=str(e), user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile",
            )


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: UserResponse = Depends(get_current_user_dependency),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Change user password.

    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service

    Returns:
        Success message

    Raises:
        HTTPException: If password change fails
    """
    with log_api_request(logger, "PUT", "/me/password", user_id=current_user.id):
        try:
            success = auth_service.change_password(
                current_user.id,
                password_data.current_password,
                password_data.new_password,
            )

            if success:
                logger.info("Password changed successfully", user_id=current_user.id)
                return {"message": "Password changed successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to change password",
                )
        except AuthenticationError as e:
            logger.warning(
                "Password change failed: authentication error",
                error=e.message,
                user_id=current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message
            )
        except NotFoundError as e:
            logger.warning(
                "User not found for password change", user_id=current_user.id
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        except Exception as e:
            logger.error(
                "Password change failed", error=str(e), user_id=current_user.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password",
            )


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """
    Get user statistics.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User statistics
    """
    with log_api_request(logger, "GET", "/me/stats", user_id=current_user.id):
        try:
            from ...repositories.note_repository import NoteRepository

            note_repo = NoteRepository(db)
            stats = note_repo.get_stats(current_user.id)

            # Add user-specific stats
            user_stats = UserStats(
                total_notes=stats["total_notes"],
                active_notes=stats["active_notes"],
                archived_notes=stats["archived_notes"],
                created_at=current_user.created_at,
                last_login=current_user.last_login,
            )

            logger.info("User stats retrieved successfully", user_id=current_user.id)
            return user_stats
        except Exception as e:
            logger.error(
                "Failed to get user stats", error=str(e), user_id=current_user.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user statistics",
            )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    current_user: UserResponse = Depends(get_current_user_dependency),
):
    """
    Logout user (client-side token invalidation).

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    with log_api_request(logger, "POST", "/logout", user_id=current_user.id):
        try:
            logger.info("User logged out successfully", user_id=current_user.id)
            return {"message": "Logged out successfully"}
        except Exception as e:
            logger.error("Logout failed", error=str(e), user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed",
            )


# OAuth2 scheme for JWT tokens
