#!/usr/bin/env python
"""
Script de prueba para verificar rate limiting
Ejecutar con el servidor de desarrollo corriendo:
    python test_ratelimit.py
"""

import requests
import time
import json

API_BASE_URL = 'http://127.0.0.1:8000/api'

def test_login_rate_limit():
    """
    Probar rate limiting en login (límite: 5/min)
    """
    print("\n" + "="*60)
    print("TEST: Rate Limiting en Login (5 intentos por minuto)")
    print("="*60)

    endpoint = f"{API_BASE_URL}/auth/login/"
    credentials = {
        "account_number": "9999999",  # Cuenta que no existe
        "password": "wrongpassword"
    }

    print(f"\nEnviando 7 solicitudes a {endpoint}")
    print("Esperado: Primeras 5 pasan, las siguientes 2 reciben 429\n")

    for i in range(1, 8):
        try:
            response = requests.post(endpoint, json=credentials, timeout=5)

            if response.status_code == 429:
                print(f"[{i}] ❌ 429 TOO MANY REQUESTS - Rate limit alcanzado!")
                print(f"    Respuesta: {response.json()}")
            elif response.status_code == 400:
                print(f"[{i}] ✓ 400 BAD REQUEST - Solicitud procesada (credenciales inválidas)")
            else:
                print(f"[{i}] ✓ {response.status_code} - Solicitud procesada")

        except requests.exceptions.ConnectionError:
            print(f"[{i}] ❌ Error: No se pudo conectar al servidor")
            print("    Asegúrate de que el servidor esté corriendo:")
            print("    cd backend && python manage.py runserver")
            break
        except Exception as e:
            print(f"[{i}] ❌ Error: {e}")

        time.sleep(0.5)  # Pequeña pausa entre solicitudes

def test_check_auth_rate_limit():
    """
    Probar rate limiting en check-auth (límite: 30/min)
    """
    print("\n" + "="*60)
    print("TEST: Rate Limiting en Check Auth (30 por minuto)")
    print("="*60)

    endpoint = f"{API_BASE_URL}/auth/check-auth/"

    print(f"\nEnviando 32 solicitudes a {endpoint}")
    print("Esperado: Primeras 30 pasan, las siguientes 2 reciben 429\n")

    success_count = 0
    rate_limited_count = 0

    for i in range(1, 33):
        try:
            response = requests.get(endpoint, timeout=5)

            if response.status_code == 429:
                rate_limited_count += 1
                if rate_limited_count == 1:  # Solo mostrar el primero
                    print(f"[{i}] ❌ 429 - Rate limit alcanzado!")
                elif rate_limited_count <= 3:
                    print(f"[{i}] ❌ 429")
            elif response.status_code == 200:
                success_count += 1
                if success_count <= 3 or success_count == 30:  # Mostrar algunos
                    print(f"[{i}] ✓ 200 - OK")

        except requests.exceptions.ConnectionError:
            print(f"[{i}] ❌ Error: Servidor no disponible")
            break
        except Exception as e:
            print(f"[{i}] ❌ Error: {e}")
            break

        if i % 10 == 0:
            print(f"    ... {i} solicitudes enviadas ...")

    print(f"\nResultado:")
    print(f"  - Exitosas: {success_count}")
    print(f"  - Rate limited: {rate_limited_count}")

def main():
    print("\n" + "#"*60)
    print("# PRUEBAS DE RATE LIMITING - MAC Attendance")
    print("#"*60)
    print("\nAsegúrate de que el servidor esté corriendo:")
    print("  cd backend && python manage.py runserver\n")

    input("Presiona ENTER para comenzar las pruebas...")

    # Probar login rate limit
    test_login_rate_limit()

    print("\n\nEsperando 5 segundos antes del siguiente test...")
    time.sleep(5)

    # Probar check-auth rate limit
    test_check_auth_rate_limit()

    print("\n" + "="*60)
    print("PRUEBAS COMPLETADAS")
    print("="*60)
    print("\nNOTA: Si necesitas desactivar rate limiting para testing:")
    print("  1. Agregar RATELIMIT_ENABLE=False en .env")
    print("  2. O cambiar block=False en los decoradores\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")