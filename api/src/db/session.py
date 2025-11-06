"""
Database session management
Re-export get_db from base for backwards compatibility
"""
from .base import get_db

__all__ = ["get_db"]
