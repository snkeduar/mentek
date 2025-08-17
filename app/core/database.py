import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection_params = {
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "database": settings.DATABASE_NAME,
            "user": settings.DATABASE_USER,
            "password": settings.DATABASE_PASSWORD,
        }
    
    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """Context manager para conexiones a la base de datos"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            conn.autocommit = False
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, connection: psycopg2.extensions.connection) -> Generator[psycopg2.extras.RealDictCursor, None, None]:
        """Context manager para cursores"""
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            yield cursor
        finally:
            if cursor:
                cursor.close()

# Instancia global
db_connection = DatabaseConnection()

def get_db_connection():
    """Dependency para obtener conexión a la base de datos"""
    return db_connection