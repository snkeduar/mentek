# app/core/database.py
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import NullPool
import logging

from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Base para los modelos
Base = declarative_base()

# =============================================================================
# CONFIGURACIÓN ASÍNCRONA (Principal - Para FastAPI)
# =============================================================================

# Crear engine asíncrono
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Mostrar queries SQL en desarrollo
    echo_pool=settings.DEBUG,  # Mostrar info del pool de conexiones
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=3600,  # Reciclar conexiones cada hora
    pool_size=10,  # Número de conexiones en el pool
    max_overflow=20,  # Conexiones adicionales permitidas
)

# Crear session factory asíncrona
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# =============================================================================
# CONFIGURACIÓN SÍNCRONA (Para Alembic y operaciones síncronas)
# =============================================================================

# Crear engine síncrono
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

# Crear session factory síncrona
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# =============================================================================
# DEPENDENCIAS PARA FASTAPI
# =============================================================================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia para obtener una sesión asíncrona de base de datos.
    Se usa en los endpoints de FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Generator[Session, None, None]:
    """
    Dependencia para obtener una sesión síncrona de base de datos.
    Se usa principalmente para migraciones y scripts.
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

async def check_database_connection() -> bool:
    """
    Verifica si la conexión a la base de datos está funcionando.
    """
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def close_database_connections():
    """
    Cierra todas las conexiones de base de datos.
    Se llama al shutdown de la aplicación.
    """
    try:
        await async_engine.dispose()
        sync_engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


def create_database_tables():
    """
    Crea todas las tablas definidas en los modelos.
    Solo para desarrollo - en producción usar Alembic.
    """
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_database_tables():
    """
    Elimina todas las tablas.
    ¡USAR CON PRECAUCIÓN! Solo para testing y desarrollo.
    """
    try:
        Base.metadata.drop_all(bind=sync_engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


# =============================================================================
# FUNCIONES PARA STORED PROCEDURES
# =============================================================================

async def execute_stored_procedure(
    procedure_name: str, 
    parameters: dict = None
) -> list:
    """
    Ejecuta un stored procedure de forma asíncrona.
    
    Args:
        procedure_name: Nombre del stored procedure
        parameters: Parámetros del stored procedure
    
    Returns:
        Lista con los resultados del stored procedure
    """
    async with AsyncSessionLocal() as session:
        try:
            # Construir los parámetros
            if parameters:
                param_list = [f":{key}" for key in parameters.keys()]
                query = f"SELECT * FROM {procedure_name}({', '.join(param_list)})"
            else:
                query = f"SELECT * FROM {procedure_name}()"
            
            result = await session.execute(text(query), parameters or {})
            rows = result.fetchall()
            
            # Convertir a lista de diccionarios
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error executing stored procedure {procedure_name}: {e}")
            raise


def execute_stored_procedure_sync(
    procedure_name: str, 
    parameters: dict = None
) -> list:
    """
    Ejecuta un stored procedure de forma síncrona.
    """
    with SessionLocal() as session:
        try:
            if parameters:
                param_list = [f":{key}" for key in parameters.keys()]
                query = f"SELECT * FROM {procedure_name}({', '.join(param_list)})"
            else:
                query = f"SELECT * FROM {procedure_name}()"
            
            result = session.execute(text(query), parameters or {})
            rows = result.fetchall()
            
            # Convertir a lista de diccionarios
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error executing stored procedure {procedure_name}: {e}")
            raise


# =============================================================================
# CONTEXTO PARA TRANSACCIONES
# =============================================================================

class DatabaseTransaction:
    """
    Context manager para manejar transacciones de base de datos.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            await self.session.commit()
            logger.debug("Transaction committed successfully")


async def get_database_transaction() -> AsyncGenerator[DatabaseTransaction, None]:
    """
    Dependencia para obtener una transacción de base de datos.
    """
    async with AsyncSessionLocal() as session:
        async with DatabaseTransaction(session) as transaction:
            yield transaction