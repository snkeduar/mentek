"""
Capa de repositorio - Acceso a datos
"""

from .base import BaseRepository
from .user_repository import UserRepository

__all__ = ["BaseRepository", "UserRepository"]