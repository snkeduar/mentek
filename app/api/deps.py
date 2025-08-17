from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db_connection, DatabaseConnection
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.core.security import verify_password
from app.config import settings
from app.schemas.user import TokenData
from app.models.user import User

security = HTTPBearer()

# Dependencias para inyección de dependencias
def get_user_repository(db_connection: DatabaseConnection = Depends(get_db_connection)) -> UserRepository:
    return UserRepository(db_connection)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await user_service.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.active or current_user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user