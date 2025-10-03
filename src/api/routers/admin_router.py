"""
Admin router for system management and configuration.

This module provides administrative endpoints for managing system settings,
log levels, and other administrative functions.
"""

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ...core.config import settings
from ...core.logging import (
    get_current_log_level,
    get_logger,
    list_configured_modules,
    set_log_level,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class LogLevelRequest(BaseModel):
    """Request model for setting log levels."""

    level: str
    module: Optional[str] = None


class LogLevelResponse(BaseModel):
    """Response model for log level operations."""

    success: bool
    message: str
    current_level: str
    module: Optional[str] = None


class SystemInfoResponse(BaseModel):
    """Response model for system information."""

    environment: str
    debug_mode: bool
    log_level: str
    log_format: str
    configured_modules: Dict[str, str]
    user_context_enabled: bool
    request_context_enabled: bool


@router.get("/system-info", response_model=SystemInfoResponse)
async def get_system_info():
    """
    Get current system configuration information.

    Returns:
        SystemInfoResponse: Current system configuration
    """
    try:
        configured_modules = list_configured_modules()

        return SystemInfoResponse(
            environment=settings.environment,
            debug_mode=settings.debug,
            log_level=settings.log_level,
            log_format=settings.log_format,
            configured_modules=configured_modules,
            user_context_enabled=settings.enable_user_context,
            request_context_enabled=settings.enable_request_context,
        )
    except Exception as e:
        logger.error("Failed to get system info", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system information",
        )


@router.post("/log-level", response_model=LogLevelResponse)
async def set_log_level_endpoint(request: LogLevelRequest):
    """
    Set log level for a specific module or globally.

    Args:
        request: Log level request with level and optional module

    Returns:
        LogLevelResponse: Result of the log level change
    """
    try:
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if request.level.upper() not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid log level. Must be one of: {valid_levels}",
            )

        # Set the log level
        set_log_level(request.level.upper(), request.module)

        # Get current level to confirm
        current_level = get_current_log_level(request.module)

        message = f"Log level set to {request.level.upper()}"
        if request.module:
            message += f" for module '{request.module}'"
        else:
            message += " globally"

        logger.info(
            "Log level changed",
            new_level=request.level.upper(),
            module=request.module or "global",
            changed_by="admin_api",
        )

        return LogLevelResponse(
            success=True,
            message=message,
            current_level=current_level,
            module=request.module,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to set log level",
            error=str(e),
            level=request.level,
            module=request.module,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set log level",
        )


@router.get("/log-level", response_model=LogLevelResponse)
async def get_log_level(module: Optional[str] = None):
    """
    Get current log level for a specific module or globally.

    Args:
        module: Optional module name. If None, returns global log level

    Returns:
        LogLevelResponse: Current log level information
    """
    try:
        current_level = get_current_log_level(module)

        return LogLevelResponse(
            success=True,
            message=f"Current log level: {current_level}",
            current_level=current_level,
            module=module,
        )

    except Exception as e:
        logger.error("Failed to get log level", error=str(e), module=module)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get log level",
        )


@router.get("/modules", response_model=Dict[str, str])
async def list_modules():
    """
    List all configured modules and their log levels.

    Returns:
        Dict[str, str]: Dictionary mapping module names to their log levels
    """
    try:
        modules = list_configured_modules()
        return modules

    except Exception as e:
        logger.error("Failed to list modules", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list configured modules",
        )


@router.post("/reset-logging")
async def reset_logging():
    """
    Reset all log levels to their default configuration.

    Returns:
        dict: Result of the reset operation
    """
    try:
        from ...core.logging import reset_log_levels

        reset_log_levels()

        logger.info("Logging configuration reset to defaults", reset_by="admin_api")

        return {"success": True, "message": "Logging configuration reset to defaults"}

    except Exception as e:
        logger.error("Failed to reset logging", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset logging configuration",
        )
