from typing import Optional, List
import logging
from datetime import date
import psycopg2
from psycopg2.extras import RealDictCursor

from app.repositories.base import BaseRepository
from app.models.user import User
from app.core.database import DatabaseConnection

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
    
    async def create(self, user: User) -> User:
        """Crear un nuevo usuario usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_create_user', [
                        user.username,
                        user.email,
                        user.password_hash,
                        user.first_name,
                        user.last_name,
                        user.avatar_url,
                        user.preferred_language,
                        user.timezone,
                        user.created_by
                    ])
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_get_user_by_id', [user_id])
                    result = cursor.fetchone()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
            raise
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por username usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_get_user_by_username', [username])
                    result = cursor.fetchone()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_get_user_by_email', [email])
                    result = cursor.fetchone()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener todos los usuarios usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_get_all_users', [skip, limit])
                    results = cursor.fetchall()
                    
                    return [User.from_dict(dict(row)) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error getting all users: {e}")
            raise
    
    async def update(self, user_id: int, user: User) -> Optional[User]:
        """Actualizar usuario usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_update_user', [
                        user_id,
                        user.username,
                        user.email,
                        user.password_hash,
                        user.first_name,
                        user.last_name,
                        user.avatar_url,
                        user.preferred_language,
                        user.timezone,
                        user.updated_by
                    ])
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    async def update_game_stats(self, user_id: int, total_points: int = None, 
                               current_streak: int = None, max_streak: int = None, 
                               daily_lives: int = None, updated_by: int = None) -> Optional[User]:
        """Actualizar estadísticas del juego usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_update_user_game_stats', [
                        user_id,
                        total_points,
                        current_streak,
                        max_streak,
                        daily_lives,
                        updated_by
                    ])
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error updating user game stats {user_id}: {e}")
            raise
    
    async def delete(self, user_id: int, deleted_by: int = None) -> bool:
        """Eliminar usuario (soft delete) usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_delete_user', [user_id, deleted_by])
                    result = cursor.fetchone()
                    conn.commit()
                    
                    # El procedimiento devuelve True si se eliminó correctamente
                    return result[0] if result else False
        except psycopg2.Error as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise
    
    async def activate_user(self, user_id: int, updated_by: int = None) -> Optional[User]:
        """Activar usuario usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_activate_user', [user_id, updated_by])
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error activating user {user_id}: {e}")
            raise
    
    async def reset_daily_lives(self, user_id: int) -> Optional[User]:
        """Resetear vidas diarias usando procedimiento almacenado"""
        try:
            with self.db_connection.get_connection() as conn:
                with self.db_connection.get_cursor(conn) as cursor:
                    cursor.callproc('sp_reset_daily_lives', [user_id])
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return User.from_dict(dict(result))
                    return None
        except psycopg2.Error as e:
            logger.error(f"Error resetting daily lives for user {user_id}: {e}")
            raise