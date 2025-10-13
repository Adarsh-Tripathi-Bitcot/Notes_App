"""
Professional FastAPI Middleware System

Enhanced middleware for comprehensive request/response logging with:
- Advanced correlation tracking
- User context extraction
- Performance monitoring
- Security event logging
- Error tracking
- Request/response logging
"""

import time
from typing import Callable, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .auth_bypass import AuthBypass
from .config import settings
from .logging import (
    RequestLoggingContext,
    generate_correlation_id,
    generate_request_id,
    generate_session_id,
    get_logger,
    log_performance,
    log_security_event,
)


class ProfessionalCorrelationMiddleware(BaseHTTPMiddleware):
    """
    Professional middleware for comprehensive request/response logging.

    Features:
    - Advanced correlation ID tracking
    - User context extraction from JWT tokens
    - Performance monitoring
    - Security event logging
    - Error tracking and reporting
    - Request/response logging
    """

    def __init__(self, app: ASGIApp, exclude_paths: Optional[List[str]] = None):
        """
        Initialize professional middleware.

        Args:
            app: ASGI application instance
            exclude_paths: Paths to exclude from detailed logging
        """
        super().__init__(app)
        self.logger = get_logger(__name__)
        self.exclude_paths = (
            exclude_paths
            if exclude_paths is not None
            else ["/health", "/metrics", "/favicon.ico"]
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process HTTP request with comprehensive logging and monitoring.

        Args:
            request: FastAPI Request object
            call_next: Next middleware/handler

        Returns:
            Response with enhanced headers and logging
        """
        # Skip detailed logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Generate unique identifiers
        correlation_id = generate_correlation_id()
        request_id = generate_request_id()
        session_id = self._get_or_create_session_id(request)

        # Extract comprehensive user context
        user_context = self._extract_user_context(request)

        # Set up comprehensive logging context
        with RequestLoggingContext(
            correlation_id=correlation_id,
            request_id=request_id,
            session_id=session_id,
            request_path=request.url.path,
            request_method=request.method,
            **user_context,
        ):
            # Log request start with performance tracking
            with log_performance(
                f"request_{request.method}_{request.url.path}", self.logger
            ):
                start_time = time.time()

                self.logger.info(
                    "Request started",
                    method=request.method,
                    path=request.url.path,
                    query_params=dict(request.query_params),
                    client_ip=self._get_client_ip(request),
                    user_agent=request.headers.get("user-agent", "unknown"),
                    content_length=request.headers.get("content-length", "0"),
                    content_type=request.headers.get("content-type", "unknown"),
                )

                try:
                    # Process request
                    response = await call_next(request)

                    # Calculate processing time
                    process_time = time.time() - start_time

                    # Log successful completion
                    self.logger.info(
                        "Request completed successfully",
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        process_time_ms=round(process_time * 1000, 2),
                        response_size=response.headers.get("content-length", "unknown"),
                    )

                    # Add enhanced headers
                    response.headers["X-Correlation-ID"] = correlation_id
                    response.headers["X-Request-ID"] = request_id
                    response.headers["X-Process-Time"] = str(
                        round(process_time * 1000, 2)
                    )

                    return response

                except Exception as exc:
                    # Calculate processing time for failed requests
                    process_time = time.time() - start_time

                    # Log security event for authentication/authorization errors
                    if exc.__class__.__name__ in [
                        "AuthenticationError",
                        "AuthorizationError",
                    ]:
                        with log_security_event(
                            "authentication_failure", "HIGH", self.logger
                        ):
                            self.logger.error(
                                "Authentication/Authorization failure",
                                method=request.method,
                                path=request.url.path,
                                error=str(exc),
                                error_type=exc.__class__.__name__,
                                process_time_ms=round(process_time * 1000, 2),
                                client_ip=self._get_client_ip(request),
                                user_agent=request.headers.get("user-agent", "unknown"),
                            )
                    else:
                        # Log general error
                        self.logger.error(
                            "Request failed",
                            method=request.method,
                            path=request.url.path,
                            error=str(exc),
                            error_type=exc.__class__.__name__,
                            process_time_ms=round(process_time * 1000, 2),
                            exc_info=True,
                        )

                    # Re-raise for error handlers
                    raise

    def _extract_user_context(self, request: Request) -> dict:
        """
        Extract comprehensive user context from JWT token.

        Args:
            request: FastAPI request object

        Returns:
            dict: User context information
        """
        # Allow authentication bypass based solely on settings/environment
        # without requiring an auth header
        if AuthBypass.is_bypass_enabled():
            return {
                "user_id": settings.test_user_id,
                "user_email": settings.test_user_email,
                "user_username": settings.test_user_username,
                "user_full_name": settings.test_user_full_name,
                "user_display_name": settings.test_user_display_name,
            }

        auth_header = request.headers.get("Authorization", "")

        # Debug logging for auth header
        if settings.log_level.upper() == "DEBUG":
            self.logger.debug(
                "Auth header analysis",
                has_auth=bool(auth_header),
                auth_type=auth_header[:10] if auth_header else "None",
                auth_length=len(auth_header),
            )

        if not auth_header.startswith("Bearer "):
            return {}

        try:
            # Extract token
            token = auth_header.split(" ")[1]

            # Parse JWT token
            from jose import jwt

            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")

            if not user_id:
                self.logger.warning("JWT token missing user ID")
                return {}

            # Get user details from database
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
                else:
                    self.logger.warning("User not found in database", user_id=user_id)
                    return {}
            finally:
                db.close()

        except Exception as e:
            # Log error but don't fail the request
            self.logger.warning(
                "Failed to extract user context",
                error=str(e),
                error_type=e.__class__.__name__,
                client_ip=self._get_client_ip(request),
            )
            return {}

    def _extract_user_id(self, request: Request) -> str:
        """
        Extract user ID from JWT token for backward compatibility.

        Args:
            request: FastAPI request object

        Returns:
            str: User ID or 'anonymous' if not found
        """
        user_context = self._extract_user_context(request)
        return user_context.get("user_id", "anonymous")

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers.

        Args:
            request: FastAPI request object

        Returns:
            str: Client IP address
        """
        # Check forwarded headers first (for load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Check CF-Connecting-IP (Cloudflare)
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip

        # Fall back to client host
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _get_or_create_session_id(self, request: Request) -> str:
        """
        Get or create session ID for request tracking.

        Args:
            request: FastAPI request object

        Returns:
            str: Session ID
        """
        # Try to get session ID from headers
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            return session_id

        # Try to get session ID from cookies
        session_id = request.cookies.get("session_id")
        if session_id:
            return session_id

        # Generate new session ID
        return generate_session_id()


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for security event logging and monitoring.
    """

    def __init__(self, app: ASGIApp):
        """Initialize security middleware."""
        super().__init__(app)
        self.logger = get_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with security monitoring."""
        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            with log_security_event("suspicious_request", "HIGH", self.logger):
                self.logger.warning(
                    "Suspicious request detected",
                    method=request.method,
                    path=request.url.path,
                    client_ip=self._get_client_ip(request),
                    user_agent=request.headers.get("user-agent", "unknown"),
                    suspicious_patterns=self._detect_suspicious_patterns(request),
                )

        return await call_next(request)

    def _is_suspicious_request(self, request: Request) -> bool:
        """Check if request appears suspicious."""
        suspicious_patterns = [
            "..",  # Path traversal
            "script",  # XSS attempts
            "union",  # SQL injection
            "select",  # SQL injection
            "drop",  # SQL injection
            "delete",  # SQL injection
            "insert",  # SQL injection
            "update",  # SQL injection
        ]

        path = request.url.path.lower()
        query = str(request.query_params).lower()

        for pattern in suspicious_patterns:
            if pattern in path or pattern in query:
                return True

        return False

    def _detect_suspicious_patterns(self, request: Request) -> List[str]:
        """Detect specific suspicious patterns in request."""
        patterns = []
        path = request.url.path.lower()
        query = str(request.query_params).lower()

        suspicious_patterns = {
            "path_traversal": ["..", "../"],
            "xss": ["<script", "javascript:", "onload="],
            "sql_injection": ["union", "select", "drop", "delete", "insert", "update"],
            "command_injection": [";", "|", "&", "`", "$("],
        }

        for pattern_type, pattern_list in suspicious_patterns.items():
            for pattern in pattern_list:
                if pattern in path or pattern in query:
                    patterns.append(pattern_type)
                    break

        return patterns

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"


def setup_professional_middleware(
    app: ASGIApp, exclude_paths: Optional[List[str]] = None
):
    """
    Set up professional middleware stack on FastAPI application.

    Args:
        app: FastAPI application instance
        exclude_paths: Paths to exclude from detailed logging
    """
    # Add middleware in reverse order (LIFO)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(
        ProfessionalCorrelationMiddleware, exclude_paths=exclude_paths or []
    )

    # Middleware configured silently


# Legacy compatibility
class CorrelationMiddleware(ProfessionalCorrelationMiddleware):
    """Legacy middleware class for backward compatibility."""

    pass


class LoggingMiddleware(ProfessionalCorrelationMiddleware):
    """Legacy middleware class for backward compatibility."""

    pass


def setup_logging_middleware(app, exclude_paths: Optional[List[str]] = None):
    """Legacy function for backward compatibility."""
    setup_professional_middleware(app, exclude_paths)
