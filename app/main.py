# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import sys
from typing import Callable

from app.core.config import settings
from app.core.database import check_database_connection, close_database_connections
from app.core.security import get_security_headers
from app.utils.exceptions import LearningAppException

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# =============================================================================
# CUSTOM MIDDLEWARE
# =============================================================================

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware para medir tiempo de respuesta."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Agregar headers de seguridad
        security_headers = get_security_headers()
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        return response


# =============================================================================
# LIFESPAN EVENTS
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja eventos de inicio y cierre de la aplicación."""
    
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Verificar conexión a base de datos
    db_connected = await check_database_connection()
    if not db_connected:
        logger.error("Failed to connect to database")
        sys.exit(1)
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_database_connections()
    logger.info("Application shutdown complete")


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

def create_exception_handlers(app: FastAPI):
    """Crea los manejadores de excepciones."""
    
    @app.exception_handler(LearningAppException)
    async def learning_app_exception_handler(request: Request, exc: LearningAppException):
        """Maneja excepciones personalizadas de la aplicación."""
        logger.error(f"Application error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "type": exc.error_type,
                    "message": exc.detail,
                    "code": exc.error_code
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Maneja excepciones HTTP estándar."""
        logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "type": "http_error",
                    "message": exc.detail,
                    "code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Maneja errores de validación de requests."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": "Error de validación en los datos enviados",
                    "details": exc.errors()
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Maneja excepciones generales no capturadas."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "type": "internal_error",
                    "message": "Error interno del servidor" if settings.is_production else str(exc),
                    "code": 500
                }
            }
        )


# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_application() -> FastAPI:
    """Factory para crear la aplicación FastAPI."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Configurar CORS
    if settings.ALLOWED_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=settings.ALLOWED_METHODS,
            allow_headers=settings.ALLOWED_HEADERS,
        )
    
    # Configurar hosts confiables
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # Agregar middleware personalizado
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TimingMiddleware)
    
    if settings.DEBUG:
        app.add_middleware(LoggingMiddleware)
    
    # Configurar exception handlers
    create_exception_handlers(app)
    
    # Incluir routers
    # TODO: Agregar cuando creemos los routers
    # from app.api.v1.api import api_router
    # app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


# =============================================================================
# CREATE APP INSTANCE
# =============================================================================

app = create_application()

# =============================================================================
# BASIC ROUTES
# =============================================================================

@app.get("/")
async def root():
    """Endpoint raíz de la API."""
    return {
        "message": f"¡{settings.PROJECT_NAME} está funcionando!",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.DEBUG else "Documentación deshabilitada en producción"
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación."""
    db_status = await check_database_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "timestamp": time.time(),
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_status else "disconnected",
        "services": {
            "api": "operational",
            "database": "operational" if db_status else "error"
        }
    }


@app.get("/info")
async def app_info():
    """Información de la aplicación."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "environment": settings.ENVIRONMENT,
        "api_version": settings.API_V1_STR,
        "features": {
            "authentication": True,
            "user_management": True,
            "course_management": True,
            "exercise_system": True,
            "gamification": True,
            "progress_tracking": True
        }
    }


# =============================================================================
# DEVELOPMENT ROUTES
# =============================================================================

if settings.DEBUG:
    @app.get("/debug/config")
    async def debug_config():
        """Endpoint para debug de la configuración (solo en desarrollo)."""
        return {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "database_configured": bool(settings.DATABASE_URL),
            "cors_origins": settings.ALLOWED_ORIGINS,
            "log_level": settings.LOG_LEVEL,
            "api_prefix": settings.API_V1_STR
        }
    
    @app.get("/debug/test-db")
    async def debug_test_database():
        """Endpoint para probar la conexión a base de datos (solo en desarrollo)."""
        from app.core.database import execute_stored_procedure
        
        try:
            # Probar con un stored procedure simple
            result = await execute_stored_procedure("sp_list_users", {"p_page": 1, "p_page_size": 5})
            return {
                "database_connection": "success",
                "test_query": "sp_list_users executed successfully",
                "result_count": len(result),
                "sample_data": result[:2] if result else []
            }
        except Exception as e:
            return {
                "database_connection": "error",
                "error": str(e)
            }