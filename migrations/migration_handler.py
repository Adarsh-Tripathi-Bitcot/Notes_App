"""
Migration handler for managing database migrations.

This script provides a command-line interface for managing database migrations
using Alembic, including creating, upgrading, and downgrading migrations.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.config import settings
from src.core.database import check_database_connection, create_tables
from src.core.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


def run_command(command: list[str]) -> int:
    """
    Run a command and return the exit code.

    Args:
        command: Command to run as a list of strings

    Returns:
        Exit code of the command
    """
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return e.returncode
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


def create_database():
    """
    Create the database if it doesn't exist.

    This function attempts to create the database using the configured
    database URL. Note that this requires appropriate permissions.
    """
    try:
        # Extract database name from URL
        db_url = settings.database_url
        if "postgresql://" in db_url:
            # For PostgreSQL, we need to connect to the default database first
            # and then create our target database
            from urllib.parse import urlparse

            import psycopg2

            parsed_url = urlparse(db_url)
            db_name = parsed_url.path[1:]  # Remove leading slash

            # Connect to default database to create our target database
            default_url = db_url.replace(f"/{db_name}", "/postgres")

            conn = psycopg2.connect(default_url)
            conn.autocommit = True
            cursor = conn.cursor()

            # Check if database exists
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"Database '{db_name}' created successfully")
            else:
                print(f"Database '{db_name}' already exists")

            cursor.close()
            conn.close()

        else:
            print("Database creation not supported for this database type")
            return 1

    except Exception as e:
        print(f"Error creating database: {e}")
        return 1

    return 0


def check_connection():
    """
    Check database connection.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        if check_database_connection():
            print("Database connection successful")
            return True
        else:
            print("Database connection failed")
            return False
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


def create_migration(message: str):
    """
    Create a new migration.

    Args:
        message: Migration message/description
    """
    print(f"Creating migration: {message}")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    command = ["alembic", "revision", "--autogenerate", "-m", message]

    exit_code = run_command(command)
    if exit_code == 0:
        print("Migration created successfully")
    else:
        print("Failed to create migration")

    return exit_code


def upgrade_database():
    """
    Upgrade database to the latest migration.
    """
    print("Upgrading database...")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    command = ["alembic", "upgrade", "head"]

    exit_code = run_command(command)
    if exit_code == 0:
        print("Database upgraded successfully")
    else:
        print("Failed to upgrade database")

    return exit_code


def downgrade_database(revision: str = "base"):
    """
    Downgrade database to a specific revision.

    Args:
        revision: Target revision (default: "base")
    """
    print(f"Downgrading database to revision: {revision}")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    command = ["alembic", "downgrade", revision]

    exit_code = run_command(command)
    if exit_code == 0:
        print("Database downgraded successfully")
    else:
        print("Failed to downgrade database")

    return exit_code


def show_current_revision():
    """
    Show the current database revision.
    """
    print("Checking current database revision...")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    command = ["alembic", "current"]

    exit_code = run_command(command)
    return exit_code


def show_migration_history():
    """
    Show migration history.
    """
    print("Migration history:")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    command = ["alembic", "history", "--verbose"]

    exit_code = run_command(command)
    return exit_code


def init_database():
    """
    Initialize the database with tables.
    """
    print("Initializing database...")

    try:
        # Check connection first
        if not check_connection():
            print("Cannot connect to database. Please check your configuration.")
            return 1

        # Create tables
        create_tables()
        print("Database initialized successfully")
        return 0

    except Exception as e:
        print(f"Error initializing database: {e}")
        return 1


def main():
    """
    Main function for handling migration commands.
    """
    if len(sys.argv) < 2:
        print("Usage: python migration_handler.py <command> [options]")
        print("\nCommands:")
        print("  create-db          Create the database")
        print("  check-connection   Check database connection")
        print("  init               Initialize database with tables")
        print("  create-migration   Create a new migration")
        print("  upgrade            Upgrade database to latest migration")
        print("  downgrade          Downgrade database to specific revision")
        print("  current            Show current database revision")
        print("  history            Show migration history")
        print("\nExamples:")
        print("  python migration_handler.py create-db")
        print(
            "  python migration_handler.py create-migration --message 'Add users table'"
        )
        print("  python migration_handler.py upgrade")
        print("  python migration_handler.py downgrade base")
        return 1

    command = sys.argv[1]

    if command == "create-db":
        return create_database()
    elif command == "check-connection":
        return 0 if check_connection() else 1
    elif command == "init":
        return init_database()
    elif command == "create-migration":
        if len(sys.argv) < 4 or sys.argv[2] != "--message":
            print(
                "Usage: python migration_handler.py create-migration --message 'Migration description'"
            )
            return 1
        message = sys.argv[3]
        return create_migration(message)
    elif command == "upgrade":
        return upgrade_database()
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "base"
        return downgrade_database(revision)
    elif command == "current":
        return show_current_revision()
    elif command == "history":
        return show_migration_history()
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
