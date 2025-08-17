from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import timedelta

from app.api.deps import get_user_service, get_current_user, get_current_active_user
from app.services.user_service import UserService
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, Token, 
    UserGameStats, UserUpdateGameStats
)
from app.models.user import User
from app.core.security import create_access_token
from app.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Registrar un nuevo usuario"""
    try:
        user = await user_service.create_user(user_data)
        return UserResponse(**user.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """Autenticar usuario y generar token de acceso"""
    user = await user_service.authenticate_user(
        user_credentials.username, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Obtener información del usuario actual"""
    return UserResponse(**current_user.to_dict())

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of users to retrieve"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de usuarios (requiere autenticación)"""
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return [UserResponse(**user.to_dict()) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener usuario por ID"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user.to_dict())

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Actualizar información del usuario actual"""
    try:
        updated_user = await user_service.update_user(
            current_user.id, 
            user_update, 
            updated_by=current_user.id
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(**updated_user.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar usuario por ID (admin)"""
    try:
        updated_user = await user_service.update_user(
            user_id, 
            user_update, 
            updated_by=current_user.id
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(**updated_user.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Eliminar cuenta del usuario actual"""
    success = await user_service.delete_user(current_user.id, deleted_by=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar usuario por ID (admin)"""
    success = await user_service.delete_user(user_id, deleted_by=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.put("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
):
    """Activar usuario (admin)"""
    user = await user_service.activate_user(user_id, updated_by=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user.to_dict())

@router.get("/me/game-stats", response_model=UserGameStats)
async def get_current_user_game_stats(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Obtener estadísticas de juego del usuario actual"""
    # Verificar y resetear vidas diarias si es necesario
    user = await user_service.check_and_reset_daily_lives(current_user.id)
    
    return UserGameStats(
        total_points=user.total_points,
        current_streak=user.current_streak,
        max_streak=user.max_streak,
        daily_lives=user.daily_lives,
        lives_reset_date=user.lives_reset_date
    )

@router.put("/me/game-stats", response_model=UserGameStats)
async def update_current_user_game_stats(
    stats_update: UserUpdateGameStats,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Actualizar estadísticas de juego del usuario actual"""
    updated_user = await user_service.update_user_game_stats(
        current_user.id, 
        stats_update, 
        updated_by=current_user.id
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserGameStats(
        total_points=updated_user.total_points,
        current_streak=updated_user.current_streak,
        max_streak=updated_user.max_streak,
        daily_lives=updated_user.daily_lives,
        lives_reset_date=updated_user.lives_reset_date
    )

@router.put("/me/reset-lives", response_model=UserGameStats)
async def reset_daily_lives(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Resetear vidas diarias del usuario actual"""
    updated_user = await user_service.reset_daily_lives(current_user.id)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserGameStats(
        total_points=updated_user.total_points,
        current_streak=updated_user.current_streak,
        max_streak=updated_user.max_streak,
        daily_lives=updated_user.daily_lives,
        lives_reset_date=updated_user.lives_reset_date
    )