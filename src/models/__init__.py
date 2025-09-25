"""
Database models for Notes App.

This module contains SQLAlchemy models representing the database schema
for users, notes, and other entities in the Notes App.
"""

from .note import Note
from .user import User

__all__ = ["User", "Note"]
