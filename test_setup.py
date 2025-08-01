# test_setup.py
"""
Script para probar la configuración inicial del proyecto.
Ejecuta: python test_setup.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

async def test_configuration():
    """Prueba la configuración de la aplicación."""
    print("🔧 Probando configuración...")
    
    try:
        from app.core.config import settings
        print(f"✅ Configuración cargada correctamente")
        print(f"   - Proyecto: {settings.PROJECT_NAME}")
        print(f"   - Versión: {settings.PROJECT_VERSION}")
        print(f"   - Entorno: {settings.ENVIRONMENT}")
        print(f"   - Debug: {settings.DEBUG}")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False


async def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("\n🗄️  Probando conexión a base de datos...")
    
    try:
        from app.core.database import check_database_connection
        
        is_connected = await check_database_connection()
        if is_connected:
            print("✅ Conexión a base de datos exitosa")
            return True
        else:
            print("❌ No se pudo conectar a la base de datos")
            print("   Verifica que PostgreSQL esté ejecutándose y las credenciales sean correctas")
            return False
    except Exception as e:
        print(f"❌ Error probando base de datos: {e}")
        return False


async def test_stored_procedures():
    """Prueba la ejecución de stored procedures."""
    print("\n🔧 Probando stored procedures...")
    
    try:
        from app.core.database import execute_stored_procedure
        
        # Probar listado de usuarios
        result = await execute_stored_procedure("sp_list_users", {
            "p_page": 1,
            "p_page_size": 5
        })
        
        print(f"✅ Stored procedure ejecutado correctamente")
        print(f"   - Registros encontrados: {len(result)}")
        
        if result:
            first_record = result[0]
            print(f"   - Campos en primer registro: {list(first_record.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Error ejecutando stored procedure: {e}")
        print("   Asegúrate de que los stored procedures estén creados en la base de datos")
        return False


async def test_security_functions():
    """Prueba las funciones de seguridad."""
    print("\n🔐 Probando funciones de seguridad...")
    
    try:
        from app.core.security import (
            get_password_hash, 
            verify_password, 
            create_access_token,
            verify_access_token,
            validate_password_strength
        )
        
        # Probar hash de contraseña
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        is_valid = verify_password(password, hashed)
        
        if not is_valid:
            print("❌ Error en hash/verificación de contraseña")
            return False
        
        print("✅ Hash y verificación de contraseña funcionando")
        
        # Probar JWT
        token_data = {"sub": "123", "username": "test_user"}
        token = create_access_token(token_data)
        decoded = verify_access_token(token)
        
        if not decoded or decoded.get("sub") != "123":
            print("❌ Error en creación/verificación de JWT")
            return False
        
        print("✅ Creación y verificación de JWT funcionando")
        
        # Probar validación de contraseña
        validation = validate_password_strength("WeakPass")
        if validation["valid"]:
            print("❌ Error en validación de contraseña débil")
            return False
        
        validation = validate_password_strength("StrongPassword123!")
        if not validation["valid"]:
            print("❌ Error en validación de contraseña fuerte")
            return False
        
        print("✅ Validación de contraseñas funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en funciones de seguridad: {e}")
        return False


async def test_exceptions():
    """Prueba las excepciones personalizadas."""
    print("\n⚠️  Probando excepciones personalizadas...")
    
    try:
        from app.utils.exceptions import (
            UserNotFoundException, 
            InvalidCredentialsException,
            ValidationException
        )
        
        # Probar que las excepciones se crean correctamente
        exc1 = UserNotFoundException("test@example.com")
        exc2 = InvalidCredentialsException()
        exc3 = ValidationException("email", "formato inválido")
        
        print("✅ Excepciones personalizadas funcionando")
        print(f"   - UserNotFoundException: {exc1.detail}")
        print(f"   - InvalidCredentialsException: {exc2.detail}")
        print(f"   - ValidationException: {exc3.detail}")
        return True
        
    except Exception as e:
        print(f"❌ Error en excepciones: {e}")
        return False


async def test_fastapi_app():
    """Prueba que la aplicación FastAPI se crea correctamente."""
    print("\n🚀 Probando aplicación FastAPI...")
    
    try:
        from app.main import app
        
        # Verificar que la app se crea
        if app is None:
            print("❌ La aplicación FastAPI no se creó correctamente")
            return False
        
        print("✅ Aplicación FastAPI creada correctamente")
        print(f"   - Título: {app.title}")
        print(f"   - Versión: {app.version}")
        
        # Verificar rutas básicas
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/info"]
        
        for route in expected_routes:
            if route not in routes:
                print(f"❌ Ruta faltante: {route}")
                return False
        
        print("✅ Rutas básicas configuradas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando aplicación FastAPI: {e}")
        return False


async def main():
    """Función principal de pruebas."""
    print("🧪 PRUEBAS DE CONFIGURACIÓN INICIAL")
    print("=" * 50)
    
    tests = [
        ("Configuración", test_configuration),
        ("Base de datos", test_database_connection),
        ("Stored procedures", test_stored_procedures),
        ("Seguridad", test_security_functions),
        ("Excepciones", test_exceptions),
        ("FastAPI", test_fastapi_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El proyecto está configurado correctamente.")
        print("\nPróximos pasos:")
        print("1. Ejecutar: uvicorn app.main:app --reload")
        print("2. Abrir: http://localhost:8000")
        print("3. Ver documentación: http://localhost:8000/docs")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())