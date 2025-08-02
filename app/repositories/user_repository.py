# app/repositories/user_repository.py
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload
from datetime import date, datetime
import logging

from app.models.user import User
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository para operaciones de usuarios."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    # =============================================================================
    # MÉTODOS DE BÚSQUEDA
    # =============================================================================
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            username: Nombre de usuario
        
        Returns:
            Usuario encontrado o None
        """
        try:
            query = select(User).where(
                and_(
                    User.username == username.lower(),
                    User.active == True,
                    User.deleted_at.is_(None)
                )
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
        
        Returns:
            Usuario encontrado o None
        """
        try:
            query = select(User).where(
                and_(
                    User.email == email.lower(),
                    User.active == True,
                    User.deleted_at.is_(None)
                )
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def exists_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un username.
        
        Args:
            username: Username a verificar
            exclude_id: ID a excluir de la búsqueda (útil para updates)
        
        Returns:
            True si existe, False si no
        """
        try:
            conditions = [
                User.username == username.lower(),
                User.deleted_at.is_(None)
            ]
            
            if exclude_id:
                conditions.append(User.id != exclude_id)
            
            query = select(func.count(User.id)).where(and_(*conditions))
            result = await self.db.execute(query)
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking username existence {username}: {e}")
            return True  # Por seguridad, asumimos que existe
    
    async def exists_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un email.
        
        Args:
            email: Email a verificar
            exclude_id: ID a excluir de la búsqueda
        
        Returns:
            True si existe, False si no
        """
        try:
            conditions = [
                User.email == email.lower(),
                User.deleted_at.is_(None)
            ]
            
            if exclude_id:
                conditions.append(User.id != exclude_id)
            
            query = select(func.count(User.id)).where(and_(*conditions))
            result = await self.db.execute(query)
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking email existence {email}: {e}")
            return True  # Por seguridad, asumimos que existe
    
    # =============================================================================
    # MÉTODOS DE LISTADO Y BÚSQUEDA
    # =============================================================================
    
    async def list_users(
        self, 
        page: int = 1, 
        page_size: int = 10,
        search: Optional[str] = None,
        active_only: bool = True,
        order_by: str = "created_at"
    ) -> Dict[str, Any]:
        """
        Lista usuarios con paginación y filtros.
        
        Args:
            page: Número de página
            page_size: Tamaño de página
            search: Término de búsqueda
            active_only: Solo usuarios activos
            order_by: Campo para ordenar
        
        Returns:
            Diccionario con usuarios y metadatos de paginación
        """
        try:
            offset = (page - 1) * page_size
            
            # Condiciones base
            conditions = []
            if active_only:
                conditions.extend([
                    User.active == True,
                    User.deleted_at.is_(None)
                ])
            
            # Búsqueda
            if search:
                search_term = f"%{search}%"
                search_conditions = or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
                conditions.append(search_conditions)
            
            # Query principal
            base_query = select(User)
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            # Ordenamiento
            if hasattr(User, order_by):
                order_field = getattr(User, order_by)
                base_query = base_query.order_by(order_field.desc())
            
            # Paginación
            query = base_query.offset(offset).limit(page_size)
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            # Contar total
            count_query = select(func.count(User.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()
            
            return {
                "users": users,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return {
                "users": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
    
    async def search_users(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[User]:
        """
        Busca usuarios por término de búsqueda.
        
        Args:
            query: Término de búsqueda
            limit: Límite de resultados
        
        Returns:
            Lista de usuarios encontrados
        """
        try:
            search_term = f"%{query}%"
            sql_query = select(User).where(
                and_(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term)
                    ),
                    User.active == True,
                    User.deleted_at.is_(None)
                )
            ).limit(limit)
            
            result = await self.db.execute(sql_query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching users with query {query}: {e}")
            return []
    
    # =============================================================================
    # MÉTODOS DE GAMIFICACIÓN
    # =============================================================================
    
    async def update_points(self, user_id: int, points_to_add: int) -> bool:
        """
        Actualiza los puntos de un usuario.
        
        Args:
            user_id: ID del usuario
            points_to_add: Puntos a agregar (puede ser negativo)
        
        Returns:
            True si se actualizó correctamente
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            user.total_points = max(0, user.total_points + points_to_add)
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating points for user {user_id}: {e}")
            await self.db.rollback()
            return False
    
    async def update_streak(self, user_id: int, new_streak: int) -> bool:
        """
        Actualiza la racha de un usuario.
        
        Args:
            user_id: ID del usuario
            new_streak: Nueva racha
        
        Returns:
            True si se actualizó correctamente
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            user.current_streak = max(0, new_streak)
            if user.current_streak > user.max_streak:
                user.max_streak = user.current_streak
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating streak for user {user_id}: {e}")
            await self.db.rollback()
            return False
    
    async def reset_daily_lives(self, user_id: int) -> bool:
        """
        Resetea las vidas diarias de un usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            True si se actualizó correctamente
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            today = date.today()
            user.daily_lives = 5
            user.lives_reset_date = today
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error resetting daily lives for user {user_id}: {e}")
            await self.db.rollback()
            return False
    
    async def use_life(self, user_id: int) -> bool:
        """
        Usa una vida del usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            True si se pudo usar la vida
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            # Verificar si es un nuevo día
            today = date.today()
            if user.lives_reset_date != today:
                user.daily_lives = 5
                user.lives_reset_date = today
            
            # Verificar si tiene vidas disponibles
            if user.daily_lives <= 0:
                return False
            
            user.daily_lives -= 1
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error using life for user {user_id}: {e}")
            await self.db.rollback()
            return False
    
    # =============================================================================
    # MÉTODOS DE ESTADÍSTICAS
    # =============================================================================
    
    async def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene estadísticas de un usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Diccionario con estadísticas o None
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            # TODO: Implementar queries para estadísticas cuando tengamos otros modelos
            # Por ahora retornamos estadísticas básicas
            return {
                "id": user.id,
                "username": user.username,
                "total_points": user.total_points,
                "current_streak": user.current_streak,
                "max_streak": user.max_streak,
                "daily_lives": user.daily_lives,
                "total_courses_enrolled": 0,  # TODO: implementar
                "total_courses_completed": 0,  # TODO: implementar
                "total_exercises_completed": 0,  # TODO: implementar
                "total_achievements": 0,  # TODO: implementar
                "average_score": 0.0,  # TODO: implementar
                "time_spent_learning": 0  # TODO: implementar
            }
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return None
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene la tabla de líderes por puntos.
        
        Args:
            limit: Número de usuarios a retornar
        
        Returns:
            Lista de usuarios ordenados por puntos
        """
        try:
            query = select(User).where(
                and_(
                    User.active == True,
                    User.deleted_at.is_(None)
                )
            ).order_by(User.total_points.desc()).limit(limit)
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            leaderboard = []
            for i, user in enumerate(users, 1):
                leaderboard.append({
                    "position": i,
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "total_points": user.total_points,
                    "current_streak": user.current_streak,
                    "max_streak": user.max_streak
                })
            
            return leaderboard
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    # =============================================================================
    # SOFT DELETE
    # =============================================================================
    
    async def soft_delete(self, user_id: int, deleted_by: Optional[int] = None) -> bool:
        """
        Elimina un usuario de forma lógica.
        
        Args:
            user_id: ID del usuario a eliminar
            deleted_by: ID del usuario que ejecuta la eliminación
        
        Returns:
            True si se eliminó correctamente
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            user.active = False
            user.deleted_at = datetime.utcnow()
            user.deleted_by = deleted_by
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error soft deleting user {user_id}: {e}")
            await self.db.rollback()
            return False
    
    async def restore_user(self, user_id: int) -> bool:
        """
        Restaura un usuario eliminado.
        
        Args:
            user_id: ID del usuario a restaurar
        
        Returns:
            True si se restauró correctamente
        """
        try:
            query = select(User).where(User.id == user_id)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.active = True
            user.deleted_at = None
            user.deleted_by = None
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error restoring user {user_id}: {e}")
            await self.db.rollback()
            return False