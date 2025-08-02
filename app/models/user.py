# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, Date, TIMESTAMP, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import date

from app.core.database import Base


class User(Base):
    """Modelo de usuario."""
    
    __tablename__ = "users"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # Gamificación
    total_points = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    daily_lives = Column(Integer, default=5, nullable=False)
    lives_reset_date = Column(Date, default=date.today, nullable=False)
    
    # Configuración
    preferred_language = Column(String(10), default='es', nullable=False)
    timezone = Column(String(50), default='UTC', nullable=False)
    
    # Campos de auditoría
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones (definiremos más adelante cuando creemos otros modelos)
    # enrollments = relationship("UserCourseEnrollment", back_populates="user")
    # rewards = relationship("UserReward", back_populates="user")
    # achievements = relationship("UserAchievement", back_populates="user")
    # daily_streaks = relationship("UserDailyStreak", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Obtiene el nombre completo del usuario."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    @property
    def is_active(self) -> bool:
        """Verifica si el usuario está activo."""
        return self.active and self.deleted_at is None
    
    def has_lives_today(self) -> bool:
        """Verifica si el usuario tiene vidas disponibles hoy."""
        today = date.today()
        if self.lives_reset_date != today:
            # Reset lives if it's a new day
            return True  # Will be reset to 5 in the service
        return self.daily_lives > 0
    
    def can_play(self) -> bool:
        """Verifica si el usuario puede jugar (está activo y tiene vidas)."""
        return self.is_active and self.has_lives_today()