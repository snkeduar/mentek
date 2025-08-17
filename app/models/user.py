from datetime import datetime, date
from typing import Optional

class User:
    """Modelo de dominio para User"""
    def __init__(
        self,
        id: Optional[int] = None,
        username: str = None,
        email: str = None,
        password_hash: str = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        total_points: int = 0,
        current_streak: int = 0,
        max_streak: int = 0,
        daily_lives: int = 5,
        lives_reset_date: Optional[date] = None,
        preferred_language: str = "es",
        timezone: str = "UTC",
        created_at: Optional[datetime] = None,
        created_by: Optional[int] = None,
        updated_at: Optional[datetime] = None,
        updated_by: Optional[int] = None,
        deleted_at: Optional[datetime] = None,
        deleted_by: Optional[int] = None,
        active: bool = True
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.avatar_url = avatar_url
        self.total_points = total_points
        self.current_streak = current_streak
        self.max_streak = max_streak
        self.daily_lives = daily_lives
        self.lives_reset_date = lives_reset_date
        self.preferred_language = preferred_language
        self.timezone = timezone
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
        self.active = active
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar_url": self.avatar_url,
            "total_points": self.total_points,
            "current_streak": self.current_streak,
            "max_streak": self.max_streak,
            "daily_lives": self.daily_lives,
            "lives_reset_date": self.lives_reset_date,
            "preferred_language": self.preferred_language,
            "timezone": self.timezone,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Crea una instancia desde un diccionario"""
        return cls(**data)