# app/utils/exceptions.py
from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class LearningAppException(HTTPException):
    """Excepción base para la aplicación."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str = "application_error",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_type = error_type
        self.error_code = error_code or f"ERR_{status_code}"


# =============================================================================
# USER EXCEPTIONS
# =============================================================================

class UserNotFoundException(LearningAppException):
    """Excepción cuando no se encuentra un usuario."""
    
    def __init__(self, user_identifier: str = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {user_identifier} no encontrado".strip(),
            error_type="user_not_found",
            error_code="USER_404"
        )


class UserAlreadyExistsException(LearningAppException):
    """Excepción cuando un usuario ya existe."""
    
    def __init__(self, field: str = "email", value: str = ""):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un usuario con {field}: {value}",
            error_type="user_already_exists",
            error_code="USER_409"
        )


class UserInactiveException(LearningAppException):
    """Excepción cuando un usuario está inactivo."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta de usuario está inactiva",
            error_type="user_inactive",
            error_code="USER_403"
        )


class InvalidCredentialsException(LearningAppException):
    """Excepción para credenciales inválidas."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            error_type="invalid_credentials",
            error_code="AUTH_401",
            headers={"WWW-Authenticate": "Bearer"}
        )


class WeakPasswordException(LearningAppException):
    """Excepción para contraseñas débiles."""
    
    def __init__(self, errors: list):
        error_msg = "La contraseña no cumple con los requisitos: " + "; ".join(errors)
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
            error_type="weak_password",
            error_code="PASS_400"
        )


# =============================================================================
# AUTHENTICATION EXCEPTIONS
# =============================================================================

class TokenExpiredException(LearningAppException):
    """Excepción cuando un token ha expirado."""
    
    def __init__(self, token_type: str = "access"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"El token de {token_type} ha expirado",
            error_type="token_expired",
            error_code="TOKEN_401",
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidTokenException(LearningAppException):
    """Excepción para tokens inválidos."""
    
    def __init__(self, reason: str = "Token inválido"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=reason,
            error_type="invalid_token",
            error_code="TOKEN_401",
            headers={"WWW-Authenticate": "Bearer"}
        )


class MissingTokenException(LearningAppException):
    """Excepción cuando no se proporciona token."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere token de autenticación",
            error_type="missing_token",
            error_code="TOKEN_401",
            headers={"WWW-Authenticate": "Bearer"}
        )


# =============================================================================
# COURSE EXCEPTIONS
# =============================================================================

class CourseNotFoundException(LearningAppException):
    """Excepción cuando no se encuentra un curso."""
    
    def __init__(self, course_id: int = None):
        detail = f"Curso con ID {course_id} no encontrado" if course_id else "Curso no encontrado"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_type="course_not_found",
            error_code="COURSE_404"
        )


class CourseAlreadyEnrolledException(LearningAppException):
    """Excepción cuando un usuario ya está inscrito en un curso."""
    
    def __init__(self, course_title: str = ""):
        detail = f"Ya estás inscrito en el curso: {course_title}" if course_title else "Ya estás inscrito en este curso"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_type="course_already_enrolled",
            error_code="COURSE_409"
        )


class PremiumCourseRequiredException(LearningAppException):
    """Excepción para cursos premium sin acceso."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Este curso requiere una suscripción premium",
            error_type="premium_required",
            error_code="COURSE_402"
        )


# =============================================================================
# EXERCISE EXCEPTIONS
# =============================================================================

class ExerciseNotFoundException(LearningAppException):
    """Excepción cuando no se encuentra un ejercicio."""
    
    def __init__(self, exercise_id: int = None):
        detail = f"Ejercicio con ID {exercise_id} no encontrado" if exercise_id else "Ejercicio no encontrado"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_type="exercise_not_found",
            error_code="EXERCISE_404"
        )


class TopicNotUnlockedException(LearningAppException):
    """Excepción cuando un tema no está desbloqueado."""
    
    def __init__(self, topic_title: str = ""):
        detail = f"El tema '{topic_title}' no está desbloqueado" if topic_title else "Este tema no está desbloqueado"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_type="topic_locked",
            error_code="TOPIC_403"
        )


class NoLivesRemainingException(LearningAppException):
    """Excepción cuando no quedan vidas."""
    
    def __init__(self, reset_time: str = ""):
        detail = "No tienes vidas restantes"
        if reset_time:
            detail += f". Se restablecerán a las {reset_time}"
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_type="no_lives_remaining",
            error_code="LIVES_429"
        )


class InvalidAnswerFormatException(LearningAppException):
    """Excepción para formato de respuesta inválido."""
    
    def __init__(self, expected_format: str = ""):
        detail = "Formato de respuesta inválido"
        if expected_format:
            detail += f". Se esperaba: {expected_format}"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_type="invalid_answer_format",
            error_code="ANSWER_400"
        )


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================

class ValidationException(LearningAppException):
    """Excepción para errores de validación."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación en {field}: {message}",
            error_type="validation_error",
            error_code="VALIDATION_400"
        )


class InvalidEmailFormatException(ValidationException):
    """Excepción para formato de email inválido."""
    
    def __init__(self):
        super().__init__("email", "El formato del email no es válido")


class InvalidUsernameFormatException(ValidationException):
    """Excepción para formato de username inválido."""
    
    def __init__(self, errors: list):
        error_msg = "; ".join(errors)
        super().__init__("username", error_msg)


# =============================================================================
# PERMISSION EXCEPTIONS
# =============================================================================

class InsufficientPermissionsException(LearningAppException):
    """Excepción para permisos insuficientes."""
    
    def __init__(self, required_permission: str = ""):
        detail = "No tienes permisos suficientes para esta acción"
        if required_permission:
            detail += f". Se requiere: {required_permission}"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_type="insufficient_permissions",
            error_code="PERM_403"
        )


class AdminRequiredException(LearningAppException):
    """Excepción cuando se requieren permisos de administrador."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador para esta acción",
            error_type="admin_required",
            error_code="ADMIN_403"
        )


# =============================================================================
# DATABASE EXCEPTIONS
# =============================================================================

class DatabaseException(LearningAppException):
    """Excepción para errores de base de datos."""
    
    def __init__(self, detail: str = "Error de base de datos"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_type="database_error",
            error_code="DB_500"
        )


class StoredProcedureException(DatabaseException):
    """Excepción para errores en stored procedures."""
    
    def __init__(self, procedure_name: str, error: str):
        super().__init__(
            detail=f"Error ejecutando {procedure_name}: {error}"
        )
        self.error_code = "SP_500"


class DatabaseConnectionException(DatabaseException):
    """Excepción para errores de conexión a base de datos."""
    
    def __init__(self):
        super().__init__(
            detail="No se pudo conectar a la base de datos"
        )
        self.error_code = "DB_CONN_500"


# =============================================================================
# FILE EXCEPTIONS
# =============================================================================

class FileUploadException(LearningAppException):
    """Excepción para errores de subida de archivos."""
    
    def __init__(self, detail: str = "Error subiendo archivo"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_type="file_upload_error",
            error_code="FILE_400"
        )


class FileSizeExceededException(FileUploadException):
    """Excepción cuando el archivo excede el tamaño máximo."""
    
    def __init__(self, max_size_mb: float):
        super().__init__(
            detail=f"El archivo excede el tamaño máximo permitido de {max_size_mb}MB"
        )
        self.error_code = "FILE_SIZE_400"


class InvalidFileTypeException(FileUploadException):
    """Excepción para tipos de archivo no permitidos."""
    
    def __init__(self, allowed_types: list):
        allowed_str = ", ".join(allowed_types)
        super().__init__(
            detail=f"Tipo de archivo no permitido. Tipos permitidos: {allowed_str}"
        )
        self.error_code = "FILE_TYPE_400"


class FileNotFoundException(LearningAppException):
    """Excepción cuando no se encuentra un archivo."""
    
    def __init__(self, filename: str = ""):
        detail = f"Archivo {filename} no encontrado" if filename else "Archivo no encontrado"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_type="file_not_found",
            error_code="FILE_404"
        )


# =============================================================================
# RATE LIMITING EXCEPTIONS
# =============================================================================

class RateLimitExceededException(LearningAppException):
    """Excepción para límite de tasa excedido."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de solicitudes excedido. Intenta de nuevo en {retry_after} segundos",
            error_type="rate_limit_exceeded",
            error_code="RATE_429",
            headers={"Retry-After": str(retry_after)}
        )


# =============================================================================
# BUSINESS LOGIC EXCEPTIONS
# =============================================================================

class StreakBrokenException(LearningAppException):
    """Excepción cuando se rompe una racha."""
    
    def __init__(self, previous_streak: int):
        super().__init__(
            status_code=status.HTTP_200_OK,  # No es realmente un error
            detail=f"Se rompió tu racha de {previous_streak} días",
            error_type="streak_broken",
            error_code="STREAK_200"
        )


class InsufficientPointsException(LearningAppException):
    """Excepción cuando no hay suficientes puntos."""
    
    def __init__(self, required_points: int, current_points: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Puntos insuficientes. Requeridos: {required_points}, Actuales: {current_points}",
            error_type="insufficient_points",
            error_code="POINTS_400"
        )


class LevelNotUnlockedException(LearningAppException):
    """Excepción cuando un nivel no está desbloqueado."""
    
    def __init__(self, level_title: str = "", required_points: int = 0):
        detail = f"El nivel '{level_title}' no está desbloqueado" if level_title else "Este nivel no está desbloqueado"
        if required_points > 0:
            detail += f". Se requieren {required_points} puntos"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_type="level_locked",
            error_code="LEVEL_403"
        )


# =============================================================================
# EXTERNAL SERVICE EXCEPTIONS
# =============================================================================

class ExternalServiceException(LearningAppException):
    """Excepción para errores de servicios externos."""
    
    def __init__(self, service_name: str, detail: str = "Servicio no disponible"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error en {service_name}: {detail}",
            error_type="external_service_error",
            error_code="EXT_503"
        )


class EmailServiceException(ExternalServiceException):
    """Excepción para errores del servicio de email."""
    
    def __init__(self, detail: str = "No se pudo enviar el email"):
        super().__init__("servicio de email", detail)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def handle_database_error(func):
    """Decorator para manejar errores de base de datos."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise UserAlreadyExistsException()
            elif "not found" in str(e).lower():
                raise UserNotFoundException()
            else:
                raise DatabaseException(f"Error de base de datos: {str(e)}")
    return wrapper


def validate_positive_id(entity_id: int, entity_name: str = "Entity") -> int:
    """Valida que un ID sea positivo."""
    if entity_id < 1:
        raise ValidationException(
            field=f"{entity_name.lower()}_id",
            message="El ID debe ser un número positivo"
        )
    return entity_id


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100):
    """Valida parámetros de paginación."""
    if page < 1:
        raise ValidationException("page", "El número de página debe ser mayor a 0")
    
    if page_size < 1:
        raise ValidationException("page_size", "El tamaño de página debe ser mayor a 0")
    
    if page_size > max_page_size:
        raise ValidationException(
            "page_size", 
            f"El tamaño de página no puede ser mayor a {max_page_size}"
        )
    
    return page, page_size