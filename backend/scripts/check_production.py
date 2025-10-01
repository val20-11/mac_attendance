#!/usr/bin/env python
"""
Script de validación para verificar configuraciones de producción
Ejecutar: python check_production.py
"""

import os
import sys
from pathlib import Path

# Desactivar colores en Windows para evitar problemas de encoding
if sys.platform == 'win32':
    GREEN = ''
    YELLOW = ''
    RED = ''
    RESET = ''
    BOLD = ''
else:
    # Colores para terminal Unix
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check_env_file():
    """Verificar que existe archivo .env"""
    print(f"\n{BOLD}1. Verificando archivo .env...{RESET}")

    if not os.path.exists('.env'):
        print(f"{RED}[X] Archivo .env no encontrado{RESET}")
        print(f"{YELLOW}   Copia .env.example o .env.production.example como .env{RESET}")
        return False

    print(f"{GREEN}[OK] Archivo .env encontrado{RESET}")
    return True

def check_env_vars():
    """Verificar variables de entorno críticas"""
    print(f"\n{BOLD}2. Verificando variables de entorno...{RESET}")

    from decouple import config

    issues = []

    # SECRET_KEY
    secret_key = config('SECRET_KEY', default='')
    if not secret_key or 'django-insecure' in secret_key or 'CHANGE' in secret_key:
        print(f"{RED}[X] SECRET_KEY no configurada o insegura{RESET}")
        issues.append("Genera una nueva SECRET_KEY segura")
    else:
        print(f"{GREEN}[OK] SECRET_KEY configurada{RESET}")

    # DEBUG
    debug = config('DEBUG', default=True, cast=bool)
    if debug:
        print(f"{YELLOW}[!] DEBUG=True (OK para desarrollo, cambiar a False en produccion){RESET}")
    else:
        print(f"{GREEN}[OK] DEBUG=False (configuracion de produccion){RESET}")

    # ALLOWED_HOSTS
    allowed_hosts = config('ALLOWED_HOSTS', default='')
    if not debug and not allowed_hosts:
        print(f"{RED}[X] ALLOWED_HOSTS no configurado{RESET}")
        issues.append("Configura ALLOWED_HOSTS con tus dominios de produccion")
    else:
        print(f"{GREEN}[OK] ALLOWED_HOSTS: {allowed_hosts}{RESET}")

    return len(issues) == 0, issues

def check_security_settings():
    """Verificar configuraciones de seguridad para producción"""
    print(f"\n{BOLD}3. Verificando configuraciones de seguridad...{RESET}")

    from decouple import config
    debug = config('DEBUG', default=True, cast=bool)

    if debug:
        print(f"{YELLOW}[!] Modo desarrollo - Configuraciones de seguridad no aplicadas{RESET}")
        print(f"{YELLOW}   Esto es normal en desarrollo local{RESET}")
        return True

    # Verificar configuraciones de produccion
    ssl_redirect = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    session_secure = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
    csrf_secure = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

    all_secure = True

    if not ssl_redirect:
        print(f"{YELLOW}[!] SECURE_SSL_REDIRECT no habilitado{RESET}")
        all_secure = False
    else:
        print(f"{GREEN}[OK] SECURE_SSL_REDIRECT habilitado{RESET}")

    if not session_secure:
        print(f"{YELLOW}[!] SESSION_COOKIE_SECURE no habilitado{RESET}")
        all_secure = False
    else:
        print(f"{GREEN}[OK] SESSION_COOKIE_SECURE habilitado{RESET}")

    if not csrf_secure:
        print(f"{YELLOW}[!] CSRF_COOKIE_SECURE no habilitado{RESET}")
        all_secure = False
    else:
        print(f"{GREEN}[OK] CSRF_COOKIE_SECURE habilitado{RESET}")

    return all_secure

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    print(f"\n{BOLD}4. Verificando dependencias...{RESET}")

    try:
        import django
        print(f"{GREEN}[OK] Django {django.get_version()}{RESET}")
    except ImportError:
        print(f"{RED}[X] Django no instalado{RESET}")
        return False

    try:
        import rest_framework
        print(f"{GREEN}[OK] Django REST Framework{RESET}")
    except ImportError:
        print(f"{RED}[X] Django REST Framework no instalado{RESET}")
        return False

    try:
        import rest_framework_simplejwt
        print(f"{GREEN}[OK] Django REST Framework SimpleJWT{RESET}")
    except ImportError:
        print(f"{RED}[X] Django REST Framework SimpleJWT no instalado{RESET}")
        return False

    try:
        import corsheaders
        print(f"{GREEN}[OK] Django CORS Headers{RESET}")
    except ImportError:
        print(f"{RED}[X] Django CORS Headers no instalado{RESET}")
        return False

    return True

def main():
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}   Verificación de Configuración - MAC Attendance{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)

    all_checks_passed = True

    # Ejecutar verificaciones
    if not check_env_file():
        all_checks_passed = False

    env_ok, issues = check_env_vars()
    if not env_ok:
        all_checks_passed = False

    if not check_security_settings():
        all_checks_passed = False

    if not check_dependencies():
        all_checks_passed = False

    # Resumen
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}   RESUMEN{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    if all_checks_passed:
        print(f"{GREEN}[OK] Todas las verificaciones pasaron{RESET}")
    else:
        print(f"{YELLOW}[!] Algunas verificaciones fallaron o necesitan atencion{RESET}")
        if issues:
            print(f"\n{BOLD}Acciones requeridas:{RESET}")
            for issue in issues:
                print(f"  - {issue}")

    print(f"\n{BOLD}Siguiente paso:{RESET}")
    print(f"  Ejecuta: python manage.py check --deploy")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)