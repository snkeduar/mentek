# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================================================================
# PASSWORD HASHING
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada
    
    Returns:
        True si coinciden, False si no
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Genera un hash de la contraseña.
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        Hash de la contraseña
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Valida la fortaleza de una contraseña.
    
    Args:
        password: Contraseña a validar
    
    Returns:
        Diccionario con resultado de validación y errores
    """
    errors = []
    
    # Longitud mínima
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")
    
    # Longitud máxima
    if len(password) > 128:
        errors.append("La contraseña no puede tener más de 128 caracteres")
    
    # Al menos una letra minúscula
    if not any(c.islower() for c in password):
        errors.append("La contraseña debe contener al menos una letra minúscula")
    
    # Al menos una letra mayúscula
    if not any(c.isupper() for c in password):
        errors.append("La contraseña debe contener al menos una letra mayúscula")
    
    # Al menos un número
    if not any(c.isdigit() for c in password):
        errors.append("La contraseña debe contener al menos un número")
    
    # Al menos un carácter especial
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("La contraseña debe contener al menos un carácter especial")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "strength": _calculate_password_strength(password)
    }


def _calculate_password_strength(password: str) -> str:
    """
    Calcula la fortaleza de una contraseña.
    """
    score = 0
    
    # Longitud
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Complejidad
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    
    if score <= 2:
        return "weak"
    elif score <= 4:
        return "medium"
    else:
        return "strong"


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token de acceso JWT.
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise


def create_refresh_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token de refresh JWT.
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token de acceso.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Payload del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar que sea un token de acceso
        if payload.get("type") != "access":
            logger.warning("Invalid token type for access token")
            return None
        
        # Verificar expiración
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            logger.warning("Access token has expired")
            return None
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying access token: {e}")
        return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token de refresh.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Payload del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar que sea un token de refresh
        if payload.get("type") != "refresh":
            logger.warning("Invalid token type for refresh token")
            return None
        
        # Verificar expiración
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            logger.warning("Refresh token has expired")
            return None
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying refresh token: {e}")
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica cualquier token sin verificar el tipo.
    Útil para obtener información sin validación estricta.
    
    Args:
        token: Token JWT a decodificar
    
    Returns:
        Payload del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        return None


# =============================================================================
# TOKEN UTILITIES
# =============================================================================

def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Obtiene la fecha de expiración de un token.
    
    Args:
        token: Token JWT
    
    Returns:
        Fecha de expiración o None si no se puede obtener
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    exp = payload.get("exp")
    if not exp:
        return None
    
    return datetime.utcfromtimestamp(exp)


def is_token_expired(token: str) -> bool:
    """
    Verifica si un token ha expirado.
    
    Args:
        token: Token JWT
    
    Returns:
        True si ha expirado, False si no
    """
    expiration = get_token_expiration(token)
    if not expiration:
        return True
    
    return expiration < datetime.utcnow()


def get_token_remaining_time(token: str) -> Optional[timedelta]:
    """
    Obtiene el tiempo restante antes de que expire un token.
    
    Args:
        token: Token JWT
    
    Returns:
        Tiempo restante o None si el token es inválido
    """
    expiration = get_token_expiration(token)
    if not expiration:
        return None
    
    remaining = expiration - datetime.utcnow()
    return remaining if remaining.total_seconds() > 0 else timedelta(0)


# =============================================================================
# SECURITY UTILITIES
# =============================================================================

def generate_random_string(length: int = 32) -> str:
    """
    Genera una cadena aleatoria segura.
    
    Args:
        length: Longitud de la cadena
    
    Returns:
        Cadena aleatoria
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """
    Genera un token seguro para verificaciones, reset de password, etc.
    
    Args:
        length: Longitud del token
    
    Returns:
        Token seguro
    """
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """
    Genera un código de verificación numérico.
    
    Args:
        length: Longitud del código
    
    Returns:
        Código de verificación
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


# =============================================================================
# RATE LIMITING UTILITIES
# =============================================================================

def create_rate_limit_key(identifier: str, endpoint: str) -> str:
    """
    Crea una clave para rate limiting.
    
    Args:
        identifier: Identificador (IP, user_id, etc.)
        endpoint: Endpoint de la API
    
    Returns:
        Clave para rate limiting
    """
    return f"rate_limit:{endpoint}:{identifier}"


# =============================================================================
# SECURITY HEADERS
# =============================================================================

def get_security_headers() -> Dict[str, str]:
    """
    Obtiene headers de seguridad recomendados.
    
    Returns:
        Diccionario con headers de seguridad
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
    }


# =============================================================================
# INPUT SANITIZATION
# =============================================================================

def sanitize_input(text: str) -> str:
    """
    Sanitiza entrada de texto para prevenir inyecciones.
    
    Args:
        text: Texto a sanitizar
    
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
    
    # Remover caracteres de control
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    
    # Limitar longitud
    return sanitized[:1000]  # Máximo 1000 caracteres


def validate_email_format(email: str) -> bool:
    """
    Valida formato de email básico.
    
    Args:
        email: Email a validar
    
    Returns:
        True si el formato es válido
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    return bool(re.match(pattern, email))


def validate_username_format(username: str) -> Dict[str, Any]:
    """
    Valida formato de nombre de usuario.
    
    Args:
        username: Username a validar
    
    Returns:
        Diccionario con resultado de validación
    """
    errors = []
    
    # Longitud
    if len(username) < 3:
        errors.append("El nombre de usuario debe tener al menos 3 caracteres")
    if len(username) > 30:
        errors.append("El nombre de usuario no puede tener más de 30 caracteres")
    
    # Caracteres permitidos
    import re
    if not re.match(r'^[a-zA-Z0-9_.-]+'
    , username):
        errors.append("El nombre de usuario solo puede contener letras, números, guiones, puntos y guiones bajos")
    
    # No puede empezar con números o caracteres especiales
    if username and not username[0].isalpha():
        errors.append("El nombre de usuario debe empezar con una letra")
    
    # No puede tener caracteres especiales consecutivos
    if re.search(r'[._-]{2,}', username):
        errors.append("El nombre de usuario no puede tener caracteres especiales consecutivos")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }