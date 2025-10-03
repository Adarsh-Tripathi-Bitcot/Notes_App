"""
Authentication service for user authentication and authorization.

This module provides authentication and authorization services including
user registration, login, JWT token management, and password handling.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.exceptions import AuthenticationError, NotFoundError, ValidationError
from ..core.logging import get_logger, log_function_call
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import TokenResponse, UserCreate, UserLogin

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    """
    Service class for authentication and authorization operations.

    This class handles user authentication, JWT token management,
    and password operations following security best practices.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the authentication service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_repository = UserRepository(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Token expiration time

        Returns:
            JWT access token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiry_minutes)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token data if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None

    def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user instance

        Raises:
            ValidationError: If validation fails
            ConflictError: If user already exists
        """
        with log_function_call(logger, "register_user", email=user_data.email):
            try:
                # Check if user already exists
                existing_user = self.user_repository.get_by_email(user_data.email)
                if existing_user:
                    raise ValidationError(
                        message="User with this email already exists",
                        field="email",
                        value=user_data.email,
                    )

                if user_data.username:
                    existing_user = self.user_repository.get_by_username(
                        user_data.username
                    )
                    if existing_user:
                        raise ValidationError(
                            message="User with this username already exists",
                            field="username",
                            value=user_data.username,
                        )

                # Hash password
                hashed_password = self.get_password_hash(user_data.password)

                # Create user data
                user_dict = {
                    "email": user_data.email,
                    "username": user_data.username,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "bio": user_data.bio,
                    "hashed_password": hashed_password,
                    "is_active": True,
                    "is_verified": False,
                }

                # Create user
                user = self.user_repository.create(user_dict)

                logger.info(
                    "User registered successfully", user_id=user.id, email=user.email
                )

                return user

            except ValidationError:
                raise
            except Exception as e:
                logger.error(
                    "Failed to register user", error=str(e), email=user_data.email
                )
                raise ValidationError(
                    message="Failed to register user", details={"error": str(e)}
                )

    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            login_data: User login data

        Returns:
            User instance if authentication successful, None otherwise
        """
        with log_function_call(logger, "authenticate_user", email=login_data.email):
            try:
                # Get user by email
                user = self.user_repository.get_by_email(login_data.email)
                if not user:
                    logger.warning(
                        "Authentication failed: user not found", email=login_data.email
                    )
                    return None

                # Check if user is active
                if not user.is_active:
                    logger.warning(
                        "Authentication failed: user inactive",
                        user_id=user.id,
                        email=user.email,
                    )
                    return None

                # Verify password
                if not self.verify_password(login_data.password, user.hashed_password):
                    logger.warning(
                        "Authentication failed: invalid password",
                        user_id=user.id,
                        email=user.email,
                    )
                    return None

                # Update last login
                user.update_last_login()
                self.db.commit()

                logger.info(
                    "User authenticated successfully", user_id=user.id, email=user.email
                )
                return user

            except Exception as e:
                logger.error(
                    "Failed to authenticate user", error=str(e), email=login_data.email
                )
                return None

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """
        Login a user and return access token.

        Args:
            login_data: User login data

        Returns:
            Token response with access token

        Raises:
            AuthenticationError: If authentication fails
        """
        with log_function_call(logger, "login_user", email=login_data.email):
            try:
                # Authenticate user
                user = self.authenticate_user(login_data)
                if not user:
                    raise AuthenticationError(
                        message="Invalid email or password",
                        details={"email": login_data.email},
                    )

                # Create access token
                token_data = {
                    "sub": str(user.id),
                    "email": user.email,
                    "username": user.username,
                }

                access_token = self.create_access_token(token_data)

                # Calculate expiration time
                expires_in = settings.jwt_expiry_minutes * 60

                logger.info(
                    "User logged in successfully", user_id=user.id, email=user.email
                )

                return TokenResponse(
                    access_token=access_token,
                    token_type="bearer",
                    expires_in=expires_in,
                )

            except AuthenticationError:
                raise
            except Exception as e:
                logger.error(
                    "Failed to login user", error=str(e), email=login_data.email
                )
                raise AuthenticationError(
                    message="Login failed", details={"error": str(e)}
                )

    def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from JWT token.

        Args:
            token: JWT access token

        Returns:
            User instance if token is valid, None otherwise
        """
        with log_function_call(logger, "get_current_user"):
            try:
                # Verify token
                payload = self.verify_token(token)
                if not payload:
                    logger.warning("Invalid token provided")
                    return None

                # Get user ID from token
                user_id = payload.get("sub")
                if not user_id:
                    logger.warning("Token missing user ID")
                    return None

                # Get user from database
                user = self.user_repository.get_by_id(int(user_id))
                if not user:
                    logger.warning("User not found for token", user_id=user_id)
                    return None

                # Check if user is still active
                if not user.is_active:
                    logger.warning("User is inactive", user_id=user.id)
                    return None

                return user

            except Exception as e:
                logger.error("Failed to get current user", error=str(e))
                return None

    def refresh_token(self, token: str) -> Optional[TokenResponse]:
        """
        Refresh a JWT token.

        Args:
            token: Current JWT access token

        Returns:
            New token response if refresh successful, None otherwise
        """
        with log_function_call(logger, "refresh_token"):
            try:
                # Get current user
                user = self.get_current_user(token)
                if not user:
                    return None

                # Create new token
                token_data = {
                    "sub": str(user.id),
                    "email": user.email,
                    "username": user.username,
                }

                access_token = self.create_access_token(token_data)
                expires_in = settings.jwt_expiry_minutes * 60

                logger.info("Token refreshed successfully", user_id=user.id)

                return TokenResponse(
                    access_token=access_token,
                    token_type="bearer",
                    expires_in=expires_in,
                )

            except Exception as e:
                logger.error("Failed to refresh token", error=str(e))
                return None

    def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully, False otherwise

        Raises:
            AuthenticationError: If current password is incorrect
            NotFoundError: If user not found
        """
        with log_function_call(logger, "change_password", user_id=user_id):
            try:
                # Get user
                user = self.user_repository.get_by_id(user_id)
                if not user:
                    raise NotFoundError(resource="User", identifier=str(user_id))

                # Verify current password
                if not self.verify_password(current_password, user.hashed_password):
                    raise AuthenticationError(
                        message="Current password is incorrect",
                        details={"user_id": user_id},
                    )

                # Hash new password
                hashed_password = self.get_password_hash(new_password)

                # Update password
                update_data = {"hashed_password": hashed_password}
                updated_user = self.user_repository.update(user_id, update_data)

                if not updated_user:
                    raise NotFoundError(resource="User", identifier=str(user_id))

                logger.info("Password changed successfully", user_id=user_id)
                return True

            except (AuthenticationError, NotFoundError):
                raise
            except Exception as e:
                logger.error("Failed to change password", error=str(e), user_id=user_id)
                raise AuthenticationError(
                    message="Failed to change password",
                    details={"error": str(e), "user_id": user_id},
                )

    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.

        Args:
            user_id: User ID

        Returns:
            True if user deactivated successfully, False otherwise

        Raises:
            NotFoundError: If user not found
        """
        with log_function_call(logger, "deactivate_user", user_id=user_id):
            try:
                # Get user
                user = self.user_repository.get_by_id(user_id)
                if not user:
                    raise NotFoundError(resource="User", identifier=str(user_id))

                # Deactivate user
                user.deactivate()
                self.db.commit()

                logger.info("User deactivated successfully", user_id=user_id)
                return True

            except NotFoundError:
                raise
            except Exception as e:
                logger.error("Failed to deactivate user", error=str(e), user_id=user_id)
                raise AuthenticationError(
                    message="Failed to deactivate user",
                    details={"error": str(e), "user_id": user_id},
                )

    def verify_user(self, user_id: int) -> bool:
        """
        Verify a user account.

        Args:
            user_id: User ID

        Returns:
            True if user verified successfully, False otherwise

        Raises:
            NotFoundError: If user not found
        """
        with log_function_call(logger, "verify_user", user_id=user_id):
            try:
                # Get user
                user = self.user_repository.get_by_id(user_id)
                if not user:
                    raise NotFoundError(resource="User", identifier=str(user_id))

                # Verify user
                user.verify()
                self.db.commit()

                logger.info("User verified successfully", user_id=user_id)
                return True

            except NotFoundError:
                raise
            except Exception as e:
                logger.error("Failed to verify user", error=str(e), user_id=user_id)
                raise AuthenticationError(
                    message="Failed to verify user",
                    details={"error": str(e), "user_id": user_id},
                )
