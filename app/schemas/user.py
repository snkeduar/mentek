# app/schemas/user.py
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.security import validate_username_format, validate_password_strength


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    """Schema base para usuario."""
    username: str = Field(..., min_length=3, max_length=30, description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Correo electrónico único")
    first_name: Optional[str] = Field(None, max_length=100, description="Nombre")
    last_name: Optional[str] = Field(None, max_length=100, description="Apellido")
    preferred_language: str = Field("es", max_length=10, description="Idioma preferido")
    timezone: str = Field("UTC", max_length=50, description="Zona horaria")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        validation = validate_username_format(v)
        if not validation['valid']:
            raise ValueError('; '.join(validation['errors']))
        return v.lower()  # Convertir a minúsculas
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 100:
                raise ValueError('Nombre muy largo')
        return v


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class UserCreate(UserBase):
    """Schema para crear usuario."""
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña")
    confirm_password: str = Field(..., description="Confirmación de contraseña")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['valid']:
            raise ValueError('; '.join(validation['errors']))
        return v
    
    def validate_passwords_match(self):
        """Valida que las contraseñas coincidan."""
        if self.password != self.confirm_password:
            raise ValueError('Las contraseñas no coinciden')
        return True


class UserUpdate(BaseModel):
    """Schema para actualizar usuario."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    preferred_language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v


class UserChangePassword(BaseModel):
    """Schema para cambiar contraseña."""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nueva contraseña")
    confirm_new_password: str = Field(..., description="Confirmación de nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['valid']:
            raise ValueError('; '.join(validation['errors']))
        return v
    
    def validate_passwords_match(self):
        """Valida que las nuevas contraseñas coincidan."""
        if self.new_password != self.confirm_new_password:
            raise ValueError('Las nuevas contraseñas no coinciden')
        return True


class UserUpdateEmail(BaseModel):
    """Schema para actualizar email."""
    new_email: EmailStr = Field(..., description="Nuevo correo electrónico")
    password: str = Field(..., description="Contraseña actual para confirmar")


class UserUpdateUsername(BaseModel):
    """Schema para actualizar username."""
    new_username: str = Field(..., min_length=3, max_length=30, description="Nuevo nombre de usuario")
    password: str = Field(..., description="Contraseña actual para confirmar")
    
    @field_validator('new_username')
    @classmethod
    def validate_username(cls, v):
        validation = validate_username_format(v)
        if not validation['valid']:
            raise ValueError('; '.join(validation['errors']))
        return v.lower()


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class UserResponse(BaseModel):
    """Schema de respuesta para usuario."""
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int
    current_streak: int
    max_streak: int
    daily_lives: int
    lives_reset_date: date
    preferred_language: str
    timezone: str
    active: bool
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    full_name: Optional[str] = None
    can_play: bool = True
    
    model_config = {"from_attributes": True}
    
    def model_post_init(self, __context):
        """Post-procesar datos después de la validación."""
        # Calcular nombre completo
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        elif self.first_name:
            self.full_name = self.first_name
        elif self.last_name:
            self.full_name = self.last_name
        else:
            self.full_name = self.username
        
        # Verificar si puede jugar
        today = date.today()
        self.can_play = self.active and (
            self.lives_reset_date != today or self.daily_lives > 0
        )


class UserPublicResponse(BaseModel):
    """Schema de respuesta pública para usuario (sin información sensible)."""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int
    current_streak: int
    max_streak: int
    
    # Campos calculados
    full_name: Optional[str] = None
    
    model_config = {"from_attributes": True}
    
    def model_post_init(self, __context):
        """Post-procesar datos después de la validación."""
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        elif self.first_name:
            self.full_name = self.first_name
        elif self.last_name:
            self.full_name = self.last_name
        else:
            self.full_name = self.username


class UserStatsResponse(BaseModel):
    """Schema de respuesta para estadísticas de usuario."""
    id: int
    username: str
    total_points: int
    current_streak: int
    max_streak: int
    daily_lives: int
    total_courses_enrolled: int = 0
    total_courses_completed: int = 0
    total_exercises_completed: int = 0
    total_achievements: int = 0
    average_score: float = 0.0
    time_spent_learning: int = 0  # en minutos
    
    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema de respuesta para lista de usuarios."""
    users: list[UserPublicResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = {"from_attributes": True}


# =============================================================================
# UTILITY SCHEMAS
# =============================================================================

class UserGameStatus(BaseModel):
    """Schema para estado de juego del usuario."""
    can_play: bool
    daily_lives: int
    lives_reset_date: date
    next_life_in: Optional[int] = None  # segundos hasta la próxima vida
    time_until_reset: Optional[int] = None  # segundos hasta reset diario
    
    model_config = {"from_attributes": True}


class UserActivitySummary(BaseModel):
    """Schema para resumen de actividad del usuario."""
    exercises_completed_today: int = 0
    points_earned_today: int = 0
    time_spent_today: int = 0  # en minutos
    current_streak: int = 0
    courses_in_progress: int = 0
    recent_achievements: list[str] = []
    
    model_config = {"from_attributes": True}