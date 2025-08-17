from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, date

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    preferred_language: str = Field("es", max_length=10)
    timezone: str = Field("UTC", max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    preferred_language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserResponse(UserBase):
    id: int
    total_points: int
    current_streak: int
    max_streak: int
    daily_lives: int
    lives_reset_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]
    active: bool
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    password_hash: str
    created_by: Optional[int]
    updated_by: Optional[int]
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserGameStats(BaseModel):
    total_points: int
    current_streak: int
    max_streak: int
    daily_lives: int
    lives_reset_date: Optional[date]

class UserUpdateGameStats(BaseModel):
    total_points: Optional[int] = None
    current_streak: Optional[int] = None
    max_streak: Optional[int] = None
    daily_lives: Optional[int] = None