"""
User repository for data access operations.

This module implements the repository pattern for user-related database operations,
providing a clean abstraction layer between the service layer and data access.
"""

from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.exceptions import ConflictError, DatabaseError, NotFoundError
from ..core.logging import get_logger, log_database_operation
from ..models.user import User

logger = get_logger(__name__)


class UserRepository:
    """
    Repository class for user-related database operations.

    This class provides methods for CRUD operations on user entities,
    following the repository pattern for clean separation of concerns.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the user repository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, user_data: dict) -> User:
        """
        Create a new user.

        Args:
            user_data: Dictionary containing user data

        Returns:
            Created user instance

        Raises:
            ConflictError: If user with email or username already exists
            DatabaseError: If database operation fails
        """
        with log_database_operation(logger, "INSERT", "users", user_id=None):
            try:
                user = User(**user_data)
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)

                logger.info(
                    "User created successfully", user_id=user.id, email=user.email
                )
                return user

            except IntegrityError as e:
                self.db.rollback()
                error_msg = str(e.orig)

                if "email" in error_msg.lower():
                    raise ConflictError(
                        message="User with this email already exists",
                        details={"field": "email", "value": user_data.get("email")},
                    )
                elif "username" in error_msg.lower():
                    raise ConflictError(
                        message="User with this username already exists",
                        details={
                            "field": "username",
                            "value": user_data.get("username"),
                        },
                    )
                else:
                    raise DatabaseError(
                        message="Failed to create user due to data conflict",
                        operation="INSERT",
                        details={"error": error_msg},
                    )

            except Exception as e:
                self.db.rollback()
                logger.error("Failed to create user", error=str(e), user_data=user_data)
                raise DatabaseError(
                    message="Failed to create user",
                    operation="INSERT",
                    details={"error": str(e)},
                )

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance if found, None otherwise
        """
        with log_database_operation(logger, "SELECT", "users", user_id=user_id):
            try:
                user = self.db.query(User).filter(User.id == user_id).first()
                return user
            except Exception as e:
                logger.error("Failed to get user by ID", error=str(e), user_id=user_id)
                raise DatabaseError(
                    message="Failed to get user by ID",
                    operation="SELECT",
                    details={"error": str(e), "user_id": user_id},
                )

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: User email

        Returns:
            User instance if found, None otherwise
        """
        with log_database_operation(logger, "SELECT", "users", email=email):
            try:
                user = self.db.query(User).filter(User.email == email).first()
                return user
            except Exception as e:
                logger.error("Failed to get user by email", error=str(e), email=email)
                raise DatabaseError(
                    message="Failed to get user by email",
                    operation="SELECT",
                    details={"error": str(e), "email": email},
                )

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: Username

        Returns:
            User instance if found, None otherwise
        """
        with log_database_operation(logger, "SELECT", "users", username=username):
            try:
                user = self.db.query(User).filter(User.username == username).first()
                return user
            except Exception as e:
                logger.error(
                    "Failed to get user by username", error=str(e), username=username
                )
                raise DatabaseError(
                    message="Failed to get user by username",
                    operation="SELECT",
                    details={"error": str(e), "username": username},
                )

    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """
        Get a user by email or username.

        Args:
            identifier: Email or username

        Returns:
            User instance if found, None otherwise
        """
        with log_database_operation(logger, "SELECT", "users", identifier=identifier):
            try:
                user = (
                    self.db.query(User)
                    .filter(or_(User.email == identifier, User.username == identifier))
                    .first()
                )
                return user
            except Exception as e:
                logger.error(
                    "Failed to get user by email or username",
                    error=str(e),
                    identifier=identifier,
                )
                raise DatabaseError(
                    message="Failed to get user by email or username",
                    operation="SELECT",
                    details={"error": str(e), "identifier": identifier},
                )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ) -> List[User]:
        """
        Get all users with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            is_verified: Filter by verified status

        Returns:
            List of user instances
        """
        with log_database_operation(logger, "SELECT", "users", skip=skip, limit=limit):
            try:
                query = self.db.query(User)

                if is_active is not None:
                    query = query.filter(User.is_active == is_active)

                if is_verified is not None:
                    query = query.filter(User.is_verified == is_verified)

                users = query.offset(skip).limit(limit).all()
                return users

            except Exception as e:
                logger.error(
                    "Failed to get all users", error=str(e), skip=skip, limit=limit
                )
                raise DatabaseError(
                    message="Failed to get all users",
                    operation="SELECT",
                    details={"error": str(e), "skip": skip, "limit": limit},
                )

    def update(self, user_id: int, update_data: dict) -> Optional[User]:
        """
        Update a user.

        Args:
            user_id: User ID
            update_data: Dictionary containing update data

        Returns:
            Updated user instance if found, None otherwise

        Raises:
            ConflictError: If update would create a conflict
            DatabaseError: If database operation fails
        """
        with log_database_operation(logger, "UPDATE", "users", user_id=user_id):
            try:
                user = self.get_by_id(user_id)
                if not user:
                    raise NotFoundError(
                        resource="User",
                        identifier=str(user_id),
                        details={"user_id": user_id},
                    )

                # Check for conflicts if email or username is being updated
                if "email" in update_data:
                    existing_user = self.get_by_email(update_data["email"])
                    if existing_user and existing_user.id != user_id:
                        raise ConflictError(
                            message="User with this email already exists",
                            details={"field": "email", "value": update_data["email"]},
                        )

                if "username" in update_data and update_data["username"]:
                    existing_user = self.get_by_username(update_data["username"])
                    if existing_user and existing_user.id != user_id:
                        raise ConflictError(
                            message="User with this username already exists",
                            details={
                                "field": "username",
                                "value": update_data["username"],
                            },
                        )

                # Update user fields
                for field, value in update_data.items():
                    if hasattr(user, field):
                        setattr(user, field, value)

                self.db.commit()
                self.db.refresh(user)

                logger.info("User updated successfully", user_id=user_id)
                return user

            except ConflictError:
                self.db.rollback()
                raise
            except NotFoundError:
                raise
            except IntegrityError as e:
                self.db.rollback()
                error_msg = str(e.orig)
                raise ConflictError(
                    message="Failed to update user due to data conflict",
                    details={"error": error_msg},
                )
            except Exception as e:
                self.db.rollback()
                logger.error("Failed to update user", error=str(e), user_id=user_id)
                raise DatabaseError(
                    message="Failed to update user",
                    operation="UPDATE",
                    details={"error": str(e), "user_id": user_id},
                )

    def delete(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: User ID

        Returns:
            True if user was deleted, False if not found
        """
        with log_database_operation(logger, "DELETE", "users", user_id=user_id):
            try:
                user = self.get_by_id(user_id)
                if not user:
                    raise NotFoundError(
                        resource="User",
                        identifier=str(user_id),
                        details={"user_id": user_id},
                    )

                self.db.delete(user)
                self.db.commit()

                logger.info("User deleted successfully", user_id=user_id)
                return True

            except NotFoundError:
                raise
            except Exception as e:
                self.db.rollback()
                logger.error("Failed to delete user", error=str(e), user_id=user_id)
                raise DatabaseError(
                    message="Failed to delete user",
                    operation="DELETE",
                    details={"error": str(e), "user_id": user_id},
                )

    def count(
        self, is_active: Optional[bool] = None, is_verified: Optional[bool] = None
    ) -> int:
        """
        Count users with optional filtering.

        Args:
            is_active: Filter by active status
            is_verified: Filter by verified status

        Returns:
            Number of users matching the criteria
        """
        with log_database_operation(logger, "COUNT", "users"):
            try:
                query = self.db.query(User)

                if is_active is not None:
                    query = query.filter(User.is_active == is_active)

                if is_verified is not None:
                    query = query.filter(User.is_verified == is_verified)

                count = query.count()
                return count

            except Exception as e:
                logger.error("Failed to count users", error=str(e))
                raise DatabaseError(
                    message="Failed to count users",
                    operation="SELECT",
                    details={"error": str(e)},
                )

    def exists(self, user_id: int) -> bool:
        """
        Check if a user exists.

        Args:
            user_id: User ID

        Returns:
            True if user exists, False otherwise
        """
        with log_database_operation(logger, "EXISTS", "users", user_id=user_id):
            try:
                exists = (
                    self.db.query(User).filter(User.id == user_id).first() is not None
                )
                return exists
            except Exception as e:
                logger.error(
                    "Failed to check if user exists", error=str(e), user_id=user_id
                )
                raise DatabaseError(
                    message="Failed to check if user exists",
                    operation="SELECT",
                    details={"error": str(e), "user_id": user_id},
                )

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Search users by email, username, or name.

        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users matching the search criteria
        """
        with log_database_operation(logger, "SEARCH", "users"):
            try:
                search_filter = (
                    User.email.ilike(f"%{query}%")
                    | User.username.ilike(f"%{query}%")
                    | User.first_name.ilike(f"%{query}%")
                    | User.last_name.ilike(f"%{query}%")
                )

                users = (
                    self.db.query(User)
                    .filter(search_filter)
                    .offset(skip)
                    .limit(limit)
                    .all()
                )

                return users

            except Exception as e:
                logger.error("Failed to search users", error=str(e))
                raise DatabaseError(
                    message="Failed to search users",
                    operation="SELECT",
                    details={"error": str(e), "query": query},
                )

    def get_stats(self, is_active: Optional[bool] = None) -> dict:
        """
        Get user statistics.

        Args:
            is_active: Filter by active status

        Returns:
            Dictionary containing user statistics
        """
        with log_database_operation(logger, "STATS", "users"):
            try:
                base_query = self.db.query(User)

                if is_active is not None:
                    base_query = base_query.filter(User.is_active == is_active)

                total_users = base_query.count()
                active_users = (
                    self.db.query(User).filter(User.is_active.is_(True)).count()
                )
                verified_users = (
                    self.db.query(User).filter(User.is_verified.is_(True)).count()
                )

                return {
                    "total_users": total_users,
                    "active_users": active_users,
                    "verified_users": verified_users,
                    "inactive_users": total_users - active_users,
                    "unverified_users": total_users - verified_users,
                }

            except Exception as e:
                logger.error("Failed to get user statistics", error=str(e))
                raise DatabaseError(
                    message="Failed to get user statistics",
                    operation="SELECT",
                    details={"error": str(e)},
                )
