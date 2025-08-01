# app/core/dependencies.py
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import logging

from app.core.database import get_async_session, get_sync_session
from app.core.config import settings
from app.core.security import verify_access_token
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# =============================================================================
# DATABASE DEPENDENCIES
# =============================================================================

async def get_db() -> AsyncSession:
    """
    Dependencia principal para obtener sesión de base de datos asíncrona.
    """
    async for session in get_async_session():
        yield session


def get_db_sync() -> Session:
    """
    Dependencia para obtener sesión de base de datos síncrona.
    """
    for session in get_sync_session():
        yield session


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserResponse]:
    """
    Obtiene el usuario actual si está autenticado, sino retorna None.
    Útil para endpoints que funcionan con o sin autenticación.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_access_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Aquí implementaremos la lógica para obtener el usuario
        # Por ahora retornamos None
        # TODO: Implementar cuando tengamos el UserRepository
        return None
        
    except Exception as e:
        logger.warning(f"Error verifying optional token: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Obtiene el usuario actual autenticado.
    Lanza excepción si no está autenticado o el token es inválido.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        payload = verify_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token malformado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # TODO: Implementar cuando tengamos el UserRepository
        # user = await user_repository.get_by_id(int(user_id))
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Usuario no encontrado",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )
        
        # Por ahora retornamos un usuario dummy
        # TODO: Remover cuando implementemos el repository
        return UserResponse(
            id=int(user_id),
            username="dummy_user",
            email="dummy@example.com",
            first_name="Dummy",
            last_name="User",
            total_points=0,
            current_streak=0,
            max_streak=0,
            daily_lives=5,
            active=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Obtiene el usuario actual y verifica que esté activo.
    """
    if not current_user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user


# =============================================================================
# PERMISSION DEPENDENCIES
# =============================================================================

def require_permissions(*required_permissions: str):
    """
    Decorator para requerir permisos específicos.
    TODO: Implementar cuando tengamos sistema de roles y permisos.
    """
    def permission_dependency(
        current_user: UserResponse = Depends(get_current_active_user)
    ) -> UserResponse:
        # TODO: Implementar verificación de permisos
        # Por ahora permitimos todo
        return current_user
    
    return permission_dependency


def require_admin():
    """
    Requiere que el usuario sea administrador.
    TODO: Implementar cuando tengamos sistema de roles.
    """
    def admin_dependency(
        current_user: UserResponse = Depends(get_current_active_user)
    ) -> UserResponse:
        # TODO: Verificar si el usuario es admin
        # if not current_user.is_admin:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Se requieren permisos de administrador"
        #     )
        return current_user
    
    return admin_dependency


# =============================================================================
# PAGINATION DEPENDENCIES
# =============================================================================

def get_pagination_params(
    page: int = 1,
    page_size: int = 10,
    max_page_size: int = 100
):
    """
    Dependencia para parámetros de paginación.
    """
    def pagination_dependency():
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de página debe ser mayor a 0"
            )
        
        if page_size < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tamaño de página debe ser mayor a 0"
            )
        
        if page_size > max_page_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El tamaño de página no puede ser mayor a {max_page_size}"
            )
        
        return {"page": page, "page_size": page_size}
    
    return pagination_dependency


# =============================================================================
# VALIDATION DEPENDENCIES
# =============================================================================

def validate_id(entity_id: int, entity_name: str = "Entity"):
    """
    Valida que el ID sea válido.
    """
    if entity_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de {entity_name} inválido"
        )
    return entity_id


# =============================================================================
# UTILITY DEPENDENCIES
# =============================================================================

def get_client_ip(request):
    """
    Obtiene la IP del cliente para rate limiting y logging.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


# =============================================================================
# TESTING DEPENDENCIES
# =============================================================================

def override_get_db():
    """
    Override de la dependencia de base de datos para testing.
    Se configura en los tests.
    """
    pass


def override_get_current_user():
    """
    Override de la dependencia de usuario actual para testing.
    """
    pass