"""
Database configuration and connection management.

This module provides database connection setup, session management,
and database utilities for the Notes App using SQLAlchemy.
"""

from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)

# Create declarative base for models
Base = declarative_base()

# Database engines
engine = None
async_engine = None

# Session makers
SessionLocal = None
AsyncSessionLocal = None


def create_database_engines() -> None:
    """
    Create database engines for synchronous and asynchronous operations.

    This function initializes both sync and async database engines
    based on the configuration settings.
    """
    global engine, async_engine, SessionLocal, AsyncSessionLocal

    # Convert postgresql:// to postgresql+asyncpg:// for async operations
    async_database_url = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://"
    )

    # Create synchronous engine
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.debug,
    )

    # Create asynchronous engine
    async_engine = create_async_engine(
        async_database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.debug,
    )

    # Create session makers
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    AsyncSessionLocal = sessionmaker(
        class_=AsyncSession, autocommit=False, autoflush=False, bind=async_engine
    )

    logger.info("Database engines created successfully")


def get_db() -> Session:
    """
    Get a synchronous database session.

    This function provides a dependency for FastAPI endpoints
    that need synchronous database access.

    Yields:
        SQLAlchemy database session
    """
    if SessionLocal is None:
        create_database_engines()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an asynchronous database session.

    This function provides a dependency for FastAPI endpoints
    that need asynchronous database access.

    Yields:
        SQLAlchemy async database session
    """
    if AsyncSessionLocal is None:
        create_database_engines()

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def create_tables() -> None:
    """
    Create all database tables.

    This function creates all tables defined in the models
    using the declarative base.
    """
    if engine is None:
        create_database_engines()

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


async def create_tables_async() -> None:
    """
    Create all database tables asynchronously.

    This function creates all tables defined in the models
    using the async engine.
    """
    if async_engine is None:
        create_database_engines()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully (async)")


def drop_tables() -> None:
    """
    Drop all database tables.

    This function drops all tables defined in the models.
    Use with caution in production!
    """
    if engine is None:
        create_database_engines()

    Base.metadata.drop_all(bind=engine)
    logger.warning("Database tables dropped")


async def drop_tables_async() -> None:
    """
    Drop all database tables asynchronously.

    This function drops all tables defined in the models.
    Use with caution in production!
    """
    if async_engine is None:
        create_database_engines()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.warning("Database tables dropped (async)")


def check_database_connection() -> bool:
    """
    Check if the database connection is working.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        if engine is None:
            create_database_engines()

        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False


async def check_database_connection_async() -> bool:
    """
    Check if the async database connection is working.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        if async_engine is None:
            create_database_engines()

        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error("Async database connection failed", error=str(e))
        return False


# Initialize database engines on module import
create_database_engines()
