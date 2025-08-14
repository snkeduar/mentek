from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str  # Este campo no se almacena directamente, se hashea

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = 'es'
    timezone: Optional[str] = 'UTC'

class UserInDB(UserBase):
    id: int
    avatar_url: Optional[str]
    total_points: int
    current_streak: int
    max_streak: int
    daily_lives: int
    lives_reset_date: date
    preferred_language: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    active: bool

    class Config:
        orm_mode = True