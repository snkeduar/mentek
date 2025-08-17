# README.md
# Users API - FastAPI con Arquitectura en Capas

Una API REST completa para gestión de usuarios desarrollada con FastAPI, PostgreSQL y procedimientos almacenados, siguiendo una arquitectura en capas limpia y escalable.

## 🚀 Características

- **Arquitectura en capas**: Separación clara entre presentación, lógica de negocio y acceso a datos
- **Procedimientos almacenados**: Toda la lógica de base de datos encapsulada en procedimientos
- **Autenticación JWT**: Sistema seguro de autenticación con tokens
- **Validación robusta**: Esquemas Pydantic para validación de datos
- **Docker**: Configuración completa para desarrollo y despliegue
- **Documentación automática**: Swagger UI y ReDoc integrados
- **Auditoría completa**: Tracking de creación, modificación y eliminación
- **Soft Delete**: Eliminación lógica de registros
- **Gestión de estadísticas**: Sistema de puntos, rachas y vidas para gamificación

## 📋 Estructura del Proyecto

```
fastapi-users-api/
├── app/                     # Código de la aplicación
│   ├── api/                # Capa de presentación (endpoints)
│   ├── core/               # Configuración central y utilidades
│   ├── models/             # Modelos de dominio
│   ├── repositories/       # Capa de acceso a datos
│   ├── schemas/            # Esquemas Pydantic
│   ├── services/           # Lógica de negocio
│   └── main.py            # Aplicación principal
├── database/               # Scripts de base de datos
│   ├── init.sql           # Inicialización de tablas
│   └── procedures/        # Procedimientos almacenados
├── docker-compose.yml     # Configuración de servicios
├── Dockerfile            # Imagen de la aplicación
└── requirements.txt      # Dependencias Python
```

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **PostgreSQL**: Base de datos relacional robusta
- **Psycopg2**: Adaptador PostgreSQL para Python
- **Pydantic**: Validación y serialización de datos
- **JWT**: Autenticación con JSON Web Tokens
- **Docker**: Containerización
- **Uvicorn**: Servidor ASGI

## 🐳 Instalación y Ejecución

### Usando Docker (Recomendado)

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd fastapi-users-api
   ```

2. **Crear archivo de variables de entorno**:
   ```bash
   cp .env.example .env
   ```

3. **Ejecutar con Docker Compose**:
   ```bash
   # Levantar todos los servicios
   docker-compose up -d
   
   # O con pgAdmin (opcional)
   docker-compose --profile tools up -d
   ```

4. **Verificar que todo esté funcionando**:
   - API: http://localhost:8000
   - Documentación: http://localhost:8000/docs
   - pgAdmin: http://localhost:5050 (si se ejecutó con profile tools)

### Instalación Manual

1. **Instalar PostgreSQL** y crear la base de datos

2. **Instalar dependencias Python**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno** en `.env`

4. **Ejecutar scripts de base de datos**:
   ```bash
   psql -U postgres -d users_db -f database/init.sql
   psql -U postgres -d users_db -f database/procedures/user_procedures.sql
   ```

5. **Ejecutar la aplicación**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 Endpoints Disponibles

### Autenticación
- `POST /api/v1/users/register` - Registrar nuevo usuario
- `POST /api/v1/users/login` - Iniciar sesión

### Gestión de Usuarios
- `GET /api/v1/users/me` - Obtener perfil actual
- `PUT /api/v1/users/me` - Actualizar perfil actual
- `DELETE /api/v1/users/me` - Eliminar cuenta actual
- `GET /api/v1/users/` - Listar usuarios (requiere auth)
- `GET /api/v1/users/{user_id}` - Obtener usuario por ID
- `PUT /api/v1/users/{user_id}` - Actualizar usuario
- `DELETE /api/v1/users/{user_id}` - Eliminar usuario
- `PUT /api/v1/users/{user_id}/activate` - Activar usuario

### Estadísticas de Juego
- `GET /api/v1/users/me/game-stats` - Obtener estadísticas actuales
- `PUT /api/v1/users/me/game-stats` - Actualizar estadísticas
- `PUT /api/v1/users/me/reset-lives` - Resetear vidas diarias

## 🔧 Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y ajusta según tu entorno:

```env
# Base de datos
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=users_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

# Seguridad
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 🏗️ Arquitectura

### Capas de la Aplicación

1. **API Layer** (`app/api/`): Endpoints HTTP y validación de entrada
2. **Service Layer** (`app/services/`): Lógica de negocio
3. **Repository Layer** (`app/repositories/`): Acceso a datos
4. **Models** (`app/models/`): Entidades de dominio
5. **Schemas** (`app/schemas/`): DTOs y validación con Pydantic

### Procedimientos Almacenados

Todos los procedimientos están en `database/procedures/user_procedures.sql`:

- `sp_create_user()` - Crear usuario
- `sp_get_user_by_id()` - Obtener por ID
- `sp_get_user_by_username()` - Obtener por username
- `sp_get_user_by_email()` - Obtener por email
- `sp_get_all_users()` - Listar usuarios
- `sp_update_user()` - Actualizar usuario
- `sp_update_user_game_stats()` - Actualizar estadísticas
- `sp_delete_user()` - Soft delete
- `sp_activate_user()` - Activar usuario
- `sp_reset_daily_lives()` - Resetear vidas diarias

## 🧪 Testing

Para probar la API puedes usar:

1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc
3. **cURL** o **Postman** con los endpoints documentados

### Ejemplo de uso:

```bash
# Registrar usuario
curl -X POST "http://localhost:8000/api/v1/users/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "password123",
       "first_name": "Test",
       "last_name": "User"
     }'

# Login
curl -X POST "http://localhost:8000/api/v1/users/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "password123"
     }'
```

## 🔐 Seguridad

- Contraseñas hasheadas con bcrypt
- Tokens JWT para autenticación
- Validación de entrada con Pydantic
- Soft delete para preservar integridad referencial
- Auditoría completa de cambios

## 📝 Logs

Los logs se almacenan en el directorio `logs/` y incluyen:
- Errores de aplicación
- Errores de base de datos
- Eventos de autenticación
- Operaciones CRUD

## 🚀 Producción

Para despliegue en producción:

1. Cambiar `SECRET_KEY` por una clave segura
2. Configurar variables de entorno apropiadas
3. Usar un servidor proxy (Nginx)
4. Configurar SSL/TLS
5. Implementar respaldos de base de datos
6. Monitoreo y alertas

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.