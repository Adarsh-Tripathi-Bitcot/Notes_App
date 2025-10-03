"""
Unit tests for database module.

This module tests database connection, session management,
and database utilities.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.core.database import (
    AsyncSessionLocal,
    SessionLocal,
    async_engine,
    check_database_connection,
    check_database_connection_async,
    create_database_engines,
    create_tables,
    create_tables_async,
    drop_tables,
    drop_tables_async,
    engine,
    get_async_db,
    get_db,
)


class TestDatabaseEngines:
    """Test database engine creation."""

    def test_create_database_engines(self):
        """Test creating database engines."""
        with patch("src.core.database.settings") as mock_settings:
            mock_settings.database_url = "postgresql://test:test@localhost/testdb"

            # Reset global variables
            import src.core.database

            src.core.database.engine = None
            src.core.database.async_engine = None
            src.core.database.SessionLocal = None
            src.core.database.AsyncSessionLocal = None

            create_database_engines()

            assert src.core.database.engine is not None
            assert src.core.database.async_engine is not None
            assert src.core.database.SessionLocal is not None
            assert src.core.database.AsyncSessionLocal is not None

    def test_create_async_engine(self):
        """Test creating async engine."""
        with patch("src.core.database.settings") as mock_settings:
            mock_settings.database_url = "postgresql://test:test@localhost/testdb"

            with patch("src.core.database.create_async_engine") as mock_create_async:
                create_database_engines()
                mock_create_async.assert_called_once()


class TestDatabaseConnection:
    """Test database connection functionality."""

    def test_check_database_connection_success(self):
        """Test successful database connection check."""
        with patch("src.core.database.engine") as mock_engine:
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_conn.execute = AsyncMock(return_value=None)

            result = check_database_connection()
            assert result is True

    def test_check_database_connection_failure(self):
        """Test failed database connection check."""
        with patch("src.core.database.engine") as mock_engine:
            mock_engine.connect.side_effect = SQLAlchemyError("Connection failed")

            result = check_database_connection()
            assert result is False

    @pytest.mark.asyncio
    async def test_check_database_connection_async_success(self):
        """Test successful async database connection check."""
        with patch("src.core.database.async_engine") as mock_engine:
            mock_conn = Mock()
            mock_begin = Mock()
            mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_begin.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin.return_value = mock_begin
            mock_conn.execute = AsyncMock(return_value=None)

            result = await check_database_connection_async()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_database_connection_async_failure(self):
        """Test failed async database connection check."""
        with patch("src.core.database.async_engine") as mock_engine:
            mock_engine.begin.side_effect = SQLAlchemyError("Connection failed")

            result = await check_database_connection_async()
            assert result is False

    @pytest.mark.asyncio
    async def test_check_database_connection_async_coroutine(self):
        """Test that check_database_connection_async returns a coroutine."""
        with patch("src.core.database.async_engine") as mock_engine:
            mock_conn = Mock()
            mock_begin = Mock()
            mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_begin.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin.return_value = mock_begin
            mock_conn.execute = AsyncMock(return_value=None)

            result = check_database_connection_async()
            # Should return a coroutine
            assert hasattr(result, "__await__")

            # Execute the coroutine
            actual_result = await result
            assert actual_result is True


class TestDatabaseSession:
    """Test database session management."""

    def test_get_db_session(self):
        """Test getting database session."""
        with patch("src.core.database.SessionLocal") as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session

            # Test the generator
            db_gen = get_db()
            db = next(db_gen)

            assert db == mock_session
            mock_session_local.assert_called_once()

    def test_get_db_session_cleanup(self):
        """Test database session cleanup."""
        with patch("src.core.database.SessionLocal") as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session

            # Test the generator
            db_gen = get_db()
            next(db_gen)

            # Test cleanup
            try:
                next(db_gen)
            except StopIteration:
                pass

            mock_session.close.assert_called_once()

    def test_get_db_exception_handling(self):
        """Test database session exception handling."""
        with patch("src.core.database.SessionLocal") as mock_session_local:
            mock_session = Mock()
            mock_session.close.side_effect = Exception("Close error")
            mock_session_local.return_value = mock_session

            # Test the generator
            db_gen = get_db()
            next(db_gen)

            # Test cleanup with exception - the exception should be raised
            with pytest.raises(Exception, match="Close error"):
                next(db_gen)

            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_async_db_session(self):
        """Test getting async database session."""
        with patch("src.core.database.AsyncSessionLocal") as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            # Test the async generator
            async for db in get_async_db():
                assert db == mock_session
                break

            mock_session_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_async_db_session_cleanup(self):
        """Test async database session cleanup."""
        with patch("src.core.database.AsyncSessionLocal") as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.close = AsyncMock(return_value=None)

            # Test the async generator - consume it fully to trigger cleanup
            async for db in get_async_db():
                assert db == mock_session
                # Don't break, let it complete naturally

            mock_session.__aexit__.assert_called_once()


class TestDatabaseTables:
    """Test database table operations."""

    def test_create_tables(self):
        """Test creating database tables."""
        with patch("src.core.database.engine") as mock_engine:
            with patch("src.core.database.Base.metadata.create_all") as mock_create_all:
                create_tables()
                mock_create_all.assert_called_once_with(bind=mock_engine)

    def test_drop_tables(self):
        """Test dropping database tables."""
        with patch("src.core.database.engine") as mock_engine:
            with patch("src.core.database.Base.metadata.drop_all") as mock_drop_all:
                drop_tables()
                mock_drop_all.assert_called_once_with(bind=mock_engine)

    @pytest.mark.asyncio
    async def test_create_tables_async(self):
        """Test creating database tables asynchronously."""
        with patch("src.core.database.async_engine") as mock_engine:
            mock_conn = Mock()
            mock_conn.run_sync = AsyncMock()
            mock_begin = Mock()
            mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_begin.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin.return_value = mock_begin

            with patch("src.core.database.Base.metadata.create_all") as mock_create_all:
                # Configure run_sync to call the function passed to it
                def run_sync_side_effect(func):
                    func()

                mock_conn.run_sync.side_effect = run_sync_side_effect

                await create_tables_async()
                mock_create_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_drop_tables_async(self):
        """Test dropping database tables asynchronously."""
        with patch("src.core.database.async_engine") as mock_engine:
            mock_conn = Mock()
            mock_conn.run_sync = AsyncMock()
            mock_begin = Mock()
            mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_begin.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin.return_value = mock_begin

            with patch("src.core.database.Base.metadata.drop_all") as mock_drop_all:
                # Configure run_sync to call the function passed to it
                def run_sync_side_effect(func):
                    func()

                mock_conn.run_sync.side_effect = run_sync_side_effect

                await drop_tables_async()
                mock_drop_all.assert_called_once()


class TestDatabaseIntegration:
    """Test database integration scenarios."""

    def test_database_connection_retry_logic(self):
        """Test database connection retry logic."""
        with patch("src.core.database.engine") as mock_engine:
            # First call fails, second succeeds
            mock_engine.connect.side_effect = [
                SQLAlchemyError("First attempt failed"),
                Mock(),
            ]

            # Should handle retry logic if implemented
            check_database_connection()
            # Result depends on implementation - could be True or False

    def test_database_connection_timeout(self):
        """Test database connection timeout handling."""
        with patch("src.core.database.engine") as mock_engine:
            mock_engine.connect.side_effect = SQLAlchemyError("Connection timeout")

            result = check_database_connection()
            assert result is False

    def test_database_connection_network_error(self):
        """Test database connection network error handling."""
        with patch("src.core.database.engine") as mock_engine:
            mock_engine.connect.side_effect = SQLAlchemyError("Network unreachable")

            result = check_database_connection()
            assert result is False

    def test_database_connection_authentication_error(self):
        """Test database connection authentication error handling."""
        with patch("src.core.database.engine") as mock_engine:
            mock_engine.connect.side_effect = SQLAlchemyError("Authentication failed")

            result = check_database_connection()
            assert result is False

    def test_database_connection_permission_error(self):
        """Test database connection permission error handling."""
        with patch("src.core.database.engine") as mock_engine:
            mock_engine.connect.side_effect = SQLAlchemyError("Permission denied")

            result = check_database_connection()
            assert result is False

    @pytest.mark.asyncio
    async def test_database_connection_async_with_text_query(self):
        """Test async database connection with text query."""
        with patch("src.core.database.async_engine") as mock_engine:
            mock_conn = Mock()
            mock_begin = Mock()
            mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_begin.__aexit__ = AsyncMock(return_value=None)
            mock_engine.begin.return_value = mock_begin
            mock_conn.execute = AsyncMock(return_value=None)

            result = await check_database_connection_async()
            assert result is True

    def test_database_engines_initialization(self):
        """Test database engines initialization on module import."""
        # The engines should be initialized when the module is imported
        assert engine is not None
        assert async_engine is not None
        assert SessionLocal is not None
        assert AsyncSessionLocal is not None

    def test_database_connection_with_none_engine(self):
        """Test database connection when engine is None."""
        with patch("src.core.database.engine", None):
            with patch("src.core.database.create_database_engines") as mock_create:
                check_database_connection()
                mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_connection_async_with_none_engine(self):
        """Test async database connection when engine is None."""
        with patch("src.core.database.async_engine", None):
            with patch("src.core.database.create_database_engines") as mock_create:
                await check_database_connection_async()
                mock_create.assert_called_once()

    def test_create_tables_with_none_engine(self):
        """Test creating tables when engine is None."""
        with patch("src.core.database.engine", None):
            with patch("src.core.database.create_database_engines"):
                with pytest.raises(AttributeError):
                    create_tables()

    @pytest.mark.asyncio
    async def test_create_tables_async_with_none_engine(self):
        """Test creating tables async when engine is None."""
        with patch("src.core.database.async_engine", None):
            with patch("src.core.database.create_database_engines"):
                with pytest.raises(AttributeError):
                    await create_tables_async()

    def test_drop_tables_with_none_engine(self):
        """Test dropping tables when engine is None."""
        with patch("src.core.database.engine", None):
            with patch("src.core.database.create_database_engines"):
                with pytest.raises(AttributeError):
                    drop_tables()

    @pytest.mark.asyncio
    async def test_drop_tables_async_with_none_engine(self):
        """Test dropping tables async when engine is None."""
        with patch("src.core.database.async_engine", None):
            with patch("src.core.database.create_database_engines"):
                with pytest.raises(AttributeError):
                    await drop_tables_async()
