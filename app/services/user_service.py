from typing import Optional, List
from datetime import datetime, date
import logging

from app.services.base import BaseService
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserUpdateGameStats
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_user(self, user_data: UserCreate, created_by: int = None) -> User:
        """Crear un nuevo usuario"""
        # Verificar si el usuario ya existe
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already exists")
        
        existing_email = await self.user_repository.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already exists")
        
        # Crear el modelo de usuario
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar_url=user_data.avatar_url,
            preferred_language=user_data.preferred_language,
            timezone=user_data.timezone,
            created_by=created_by
        )
        
        return await self.user_repository.create(user)
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        user = await self.user_repository.get_by_id(user_id)
        if user and user.deleted_at is None and user.active:
            return user
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        user = await self.user_repository.get_by_username(username)
        if user and user.deleted_at is None and user.active:
            return user
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        user = await self.user_repository.get_by_email(email)
        if user and user.deleted_at is None and user.active:
            return user
        return None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener todos los usuarios activos"""
        users = await self.user_repository.get_all(skip, limit)
        # Filtrar solo usuarios activos y no eliminados
        return [user for user in users if user.deleted_at is None and user.active]
    
    async def update_user(self, user_id: int, user_update: UserUpdate, updated_by: int = None) -> Optional[User]:
        """Actualizar usuario"""
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user or existing_user.deleted_at is not None or not existing_user.active:
            return None
        
        # Verificar duplicados si se está actualizando username o email
        if user_update.username and user_update.username != existing_user.username:
            username_exists = await self.user_repository.get_by_username(user_update.username)
            if username_exists and username_exists.id != user_id:
                raise ValueError("Username already exists")
        
        if user_update.email and user_update.email != existing_user.email:
            email_exists = await self.user_repository.get_by_email(user_update.email)
            if email_exists and email_exists.id != user_id:
                raise ValueError("Email already exists")
        
        # Actualizar solo los campos proporcionados
        update_data = user_update.dict(exclude_unset=True)
        
        # Si se está actualizando la contraseña, hashearla
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        # Crear objeto User con los datos actualizados
        updated_user = User(**{
            **existing_user.to_dict(),
            **update_data,
            "updated_by": updated_by
        })
        
        return await self.user_repository.update(user_id, updated_user)
    
    async def update_user_game_stats(self, user_id: int, stats_update: UserUpdateGameStats, updated_by: int = None) -> Optional[User]:
        """Actualizar estadísticas del juego de un usuario"""
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user or existing_user.deleted_at is not None or not existing_user.active:
            return None
        
        update_data = stats_update.dict(exclude_unset=True)
        
        return await self.user_repository.update_game_stats(
            user_id=user_id,
            total_points=update_data.get("total_points"),
            current_streak=update_data.get("current_streak"),
            max_streak=update_data.get("max_streak"),
            daily_lives=update_data.get("daily_lives"),
            updated_by=updated_by
        )
    
    async def delete_user(self, user_id: int, deleted_by: int = None) -> bool:
        """Eliminar usuario (soft delete)"""
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user or existing_user.deleted_at is not None:
            return False
        
        return await self.user_repository.delete(user_id, deleted_by)
    
    async def activate_user(self, user_id: int, updated_by: int = None) -> Optional[User]:
        """Activar usuario"""
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            return None
        
        return await self.user_repository.activate_user(user_id, updated_by)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        
        if not user.active or user.deleted_at is not None:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def reset_daily_lives(self, user_id: int) -> Optional[User]:
        """Resetear vidas diarias de un usuario"""
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user or existing_user.deleted_at is not None or not existing_user.active:
            return None
        
        # Verificar si es necesario resetear las vidas (nueva fecha)
        today = date.today()
        if existing_user.lives_reset_date == today:
            return existing_user  # Ya se resetearon hoy
        
        return await self.user_repository.reset_daily_lives(user_id)
    
    async def check_and_reset_daily_lives(self, user_id: int) -> Optional[User]:
        """Verificar y resetear vidas diarias si es necesario"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        today = date.today()
        if user.lives_reset_date != today:
            return await self.reset_daily_lives(user_id)
        
        return user