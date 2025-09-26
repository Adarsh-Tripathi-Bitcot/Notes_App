"""
Logging management API endpoints.

This module provides endpoints for managing log levels dynamically at runtime.
"""

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...core.logging import (
    get_current_log_level,
    list_configured_modules,
    reset_log_levels,
    set_log_level,
)

router = APIRouter()


class LogLevelRequest(BaseModel):
    """Request model for setting log level."""

    level: str
    module: Optional[str] = None


class LogLevelResponse(BaseModel):
    """Response model for log level operations."""

    message: str
    level: Optional[str] = None
    module: Optional[str] = None


@router.get("/status", response_model=LogLevelResponse)
async def get_logging_status():
    """Get current logging status and configuration."""
    try:
        root_level = get_current_log_level()

        return LogLevelResponse(
            message="Logging status retrieved successfully",
            level=root_level,
            module="root",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get logging status: {str(e)}"
        )


@router.post("/set-level", response_model=LogLevelResponse)
async def set_logging_level(request: LogLevelRequest):
    """Set log level for a specific module or globally."""
    try:
        set_log_level(request.level, request.module)

        target = request.module or "root"
        return LogLevelResponse(
            message=f"Log level set to {request.level.upper()} for {target}",
            level=request.level.upper(),
            module=request.module,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to set log level: {str(e)}"
        )


@router.get("/level/{module_name}", response_model=LogLevelResponse)
async def get_module_log_level(module_name: str):
    """Get current log level for a specific module."""
    try:
        level = get_current_log_level(module_name)

        return LogLevelResponse(
            message=f"Log level for {module_name} is {level}",
            level=level,
            module=module_name,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get log level: {str(e)}"
        )


@router.get("/modules", response_model=Dict[str, str])
async def list_modules():
    """List all configured modules and their log levels."""
    try:
        modules = list_configured_modules()
        return modules
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list modules: {str(e)}")


@router.post("/reset", response_model=LogLevelResponse)
async def reset_logging():
    """Reset all log levels to their default configuration."""
    try:
        reset_log_levels()

        return LogLevelResponse(message="All log levels reset to default configuration")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reset log levels: {str(e)}"
        )
