"""
FastAPI Correlation Middleware

This module provides middleware for adding correlation IDs and request context
following the mentor's specifications for comprehensive request/response logging.
"""

import time
from typing import Callable, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import settings
from .logging import add_correlation_context, generate_correlation_id, get_logger


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation IDs and request context.

    This middleware:
    1. Generates unique correlation ID per request
    2. Extracts user information from headers/tokens
    3. Sets up logging context for request lifecycle
    4. Logs request start/completion with timing
    """

    def __init__(self, app: ASGIApp, exclude_paths: Optional[List[str]] = None):
        """
        Initialize middleware.

        Args:
            app: ASGI application instance
            exclude_paths: Paths to exclude from user extraction
        """
        super().__init__(app)
        self.logger = get_logger(__name__)
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process HTTP request with correlation tracking.

        Args:
            request: FastAPI Request object
            call_next: Next middleware/handler

        Returns:
            Response with correlation headers added
        """
        # Generate correlation ID
        correlation_id = generate_correlation_id()
        request_path = str(request.url.path)
        request_method = request.method

        # Extract comprehensive user context
        user_context = self._extract_user_context(request)

        # Debug logging
        self.logger.info("Extracted user context", user_context=user_context)

        # Set up logging context with all available information
        add_correlation_context(
            user_id=user_context.get("user_id"),
            request_id=request_path,
            xray_id=request_method,
            correlation_id=correlation_id,
        )

        # Log request start
        start_time = time.time()
        self.logger.info(
            "Request started",
            method=request_method,
            path=request_path,
            query_params=dict(request.query_params),
            client_ip=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent", "unknown"),
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log successful completion
            self.logger.info(
                "Request completed",
                method=request_method,
                path=request_path,
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception as exc:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time

            # Log error
            self.logger.error(
                "Request failed",
                method=request_method,
                path=request_path,
                error=str(exc),
                error_type=exc.__class__.__name__,
                process_time_ms=round(process_time * 1000, 2),
                exc_info=True,
            )

            # Re-raise for error handlers
            raise

    def _extract_user_id(self, request: Request) -> str:
        """
        Extract user ID from request headers or tokens.
        Implement based on your authentication system.

        Args:
            request: FastAPI request object

        Returns:
            str: User ID or "anonymous"
        """
        # Example implementation - adapt to your auth system
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Parse JWT token or API key to extract user ID
            # This is a placeholder - implement your token parsing logic
            return "extracted_user_id"
        return "anonymous"

    def _extract_user_context(self, request: Request) -> dict:
        """
        Extract comprehensive user context from JWT token.

        Args:
            request: FastAPI request object

        Returns:
            dict: User context information
        """
        auth_header = request.headers.get("Authorization", "")
        self.logger.debug(
            "Auth header present",
            has_auth=bool(auth_header),
            auth_type=auth_header[:10] if auth_header else "None",
        )

        if not auth_header.startswith("Bearer "):
            return {}

        try:
            # Extract token
            token = auth_header.split(" ")[1]

            # Check if auth bypass is enabled
            if settings.auth_bypass:
                return {
                    "user_id": settings.test_user_id,
                    "user_email": settings.test_user_email,
                    "user_username": settings.test_user_username,
                    "user_full_name": "Test User",
                    "user_display_name": settings.test_user_username,
                }

            # Parse JWT token to get user ID
            from jose import jwt

            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")

            if not user_id:
                return {}

            # Get user details from database using proper session management
            from src.core.database import SessionLocal
            from src.repositories.user_repository import UserRepository

            db = SessionLocal()
            try:
                user_repo = UserRepository(db)
                user = user_repo.get_by_id(int(user_id))

                if user:
                    return {
                        "user_id": str(user.id),
                        "user_email": user.email,
                        "user_username": user.username or "N/A",
                        "user_full_name": user.full_name,
                        "user_display_name": user.display_name,
                    }
            finally:
                db.close()

        except Exception as e:
            # Log error but don't fail the request
            self.logger.warning("Failed to extract user context", error=str(e))

        return {}

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers.

        Args:
            request: FastAPI request object

        Returns:
            str: Client IP address
        """
        # Check forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client host
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"


def setup_logging_middleware(app, exclude_paths: Optional[List[str]] = None):
    """
    Set up logging middleware on FastAPI application.

    Args:
        app: FastAPI application instance
        exclude_paths: Paths to exclude from user extraction
    """
    # Add middleware (processed in LIFO order)
    app.add_middleware(CorrelationMiddleware, exclude_paths=exclude_paths or [])

    logger = get_logger(__name__)
    logger.info("Logging middleware configured", correlation_enabled=True)


# Legacy middleware for backward compatibility
class LoggingMiddleware(CorrelationMiddleware):
    """
    Legacy middleware class for backward compatibility.

    This is an alias for CorrelationMiddleware to maintain existing code.
    """

    pass
