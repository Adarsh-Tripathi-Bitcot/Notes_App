"""
FastAPI main application setup.

This module configures and initializes the FastAPI application with
all necessary middleware, error handlers, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from ..core.config import settings
from ..core.database import create_tables
from ..core.error_handler import setup_error_handlers
from ..core.logging import configure_logging, get_logger
from .routers import logging_router, notes_router, user_router

# Note: Logging will be configured at startup, not at import time


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="A clean architecture Notes App built with FastAPI",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add trusted host middleware for production
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure with actual domains in production
        )

    # Setup error handlers
    setup_error_handlers(app)

    # Include routers
    app.include_router(user_router.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(notes_router.router, prefix="/api/v1/notes", tags=["notes"])
    app.include_router(
        logging_router.router, prefix="/api/v1/logging", tags=["logging"]
    )

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """
        Health check endpoint.

        Returns:
            Health status information
        """
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": "1.0.0",
            "environment": settings.environment,
        }

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """
        Root endpoint.

        Returns:
            Welcome message and API information
        """
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": "1.0.0",
            "docs_url": "/docs"
            if settings.debug
            else "Documentation not available in production",
            "health_check": "/health",
        }

    # Log application creation (logger will be available after startup)
    return app


# Create the app instance
app = create_app()


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.

    This function is called when the application starts up.
    It initializes the database and performs other startup tasks.
    """
    # Configure logging at startup
    configure_logging()
    logger = get_logger(__name__)

    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")

        # Log startup information
        logger.info(
            "Application started successfully",
            app_name=settings.app_name,
            environment=settings.environment,
            debug=settings.debug,
        )

    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.

    This function is called when the application shuts down.
    It performs cleanup tasks.
    """
    logger = get_logger(__name__)
    logger.info("Application shutting down")


# For development server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
