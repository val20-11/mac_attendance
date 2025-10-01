# Configuración de Rate Limiting

## Resumen

El proyecto implementa rate limiting (limitación de tasa) usando `django-ratelimit` para proteger los endpoints contra:
- ✅ Ataques de fuerza bruta
- ✅ Abuso de API
- ✅ Ataques DDoS
- ✅ Spam y registro masivo

## Límites Configurados por Endpoint

### Autenticación (`authentication/views.py`)

| Endpoint | Límite | Clave | Descripción |
|----------|--------|-------|-------------|
| `/api/auth/login/` | 5/min | IP | Máximo 5 intentos de login por minuto por IP |
| `/api/auth/check-auth/` | 30/min | IP | Máximo 30 verificaciones de estado por minuto por IP |
| `/api/auth/token/refresh/` | 10/min | IP | Máximo 10 renovaciones de token por minuto por IP |

**Razón**: Prevenir ataques de fuerza bruta en credenciales y enumeración de usuarios.

### Eventos (`events/views.py`)

| Endpoint | Límite | Clave | Descripción |
|----------|--------|-------|-------------|
| `/api/events/register-external/` | 3/hora | IP | Máximo 3 registros de usuarios externos por hora por IP |
| `/api/events/approve/<id>/` | 30/min | Usuario | Máximo 30 aprobaciones/rechazos por minuto por asistente |

**Razón**:
- Prevenir spam de registros externos
- Evitar abuso en aprobaciones masivas

### Asistencias (`attendance/views.py`)

| Endpoint | Límite | Clave | Descripción |
|----------|--------|-------|-------------|
| `/api/attendance/register/` (POST) | 60/min | Usuario | Máximo 60 registros de asistencia por minuto por asistente |
| `/api/attendance/student-stats/` | 30/min | Usuario | Máximo 30 consultas de estadísticas por minuto por usuario |
| `/api/attendance/recent/` | 60/min | Usuario | Máximo 60 consultas de asistencias recientes por minuto por asistente |

**Razón**:
- Balancear uso legítimo (eventos grandes con muchos estudiantes)
- Prevenir abuso y sobrecarga del servidor

## Tipos de Claves (Keys)

### `key='ip'`
- Limita por dirección IP del cliente
- Usado para endpoints públicos (login, registro)
- Protege contra ataques desde una misma IP

### `key='user'`
- Limita por usuario autenticado
- Usado para endpoints protegidos
- Permite diferentes límites por usuario

## Respuesta al Exceder el Límite

Cuando un usuario excede el límite, recibe:

```json
{
    "error": "Demasiadas solicitudes. Por favor, intenta más tarde.",
    "detail": "Has excedido el límite de solicitudes permitidas. Espera unos momentos antes de intentar nuevamente."
}
```

**HTTP Status Code**: `429 Too Many Requests`

## Configuración en settings.py

```python
# Habilitar/deshabilitar rate limiting globalmente
RATELIMIT_ENABLE = True  # False para desactivar en testing

# Backend de cache para almacenar contadores
RATELIMIT_USE_CACHE = 'default'

# Cache backend (LocMemCache en desarrollo)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ratelimit-cache',
    }
}

# Manejador de excepciones personalizado
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'mac_attendance.exceptions.custom_exception_handler',
}
```

## Formato de Rate Limits

Los límites se especifican con el formato: `cantidad/periodo`

**Ejemplos**:
- `5/m` = 5 solicitudes por minuto
- `3/h` = 3 solicitudes por hora
- `100/d` = 100 solicitudes por día
- `1000/s` = 1000 solicitudes por segundo

**Períodos válidos**:
- `s` = segundo
- `m` = minuto
- `h` = hora
- `d` = día

## Decoradores Utilizados

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    # key: Clave para agrupar (ip, user, header, etc.)
    # rate: Límite (cantidad/periodo)
    # method: Método HTTP a limitar (POST, GET, etc.)
    # block: True = bloquear, False = solo marcar (sin bloquear)
    pass
```

## Desactivar Rate Limiting (Testing)

### En .env
```bash
RATELIMIT_ENABLE=False
```

### En código (decorador)
```python
@ratelimit(key='ip', rate='5/m', method='POST', block=False)
# block=False permite que la solicitud pase pero marca el límite
```

## Monitoreo y Ajuste

### ¿Cómo saber si los límites son apropiados?

1. **Monitorear logs**: Buscar errores 429 en los logs
2. **Feedback de usuarios**: Usuarios legítimos reportando bloqueos
3. **Métricas de uso**: Analizar patrones de tráfico normales

### Ajustar límites

Si un límite es muy restrictivo:
1. Aumentar el número: `5/m` → `10/m`
2. Aumentar el período: `5/m` → `5/2m` (5 cada 2 minutos)
3. Cambiar la clave: `key='ip'` → `key='user'`

Si un límite es muy permisivo:
1. Disminuir el número
2. Disminuir el período
3. Agregar límites adicionales

## Producción: Redis Cache

Para producción con múltiples servidores, usar Redis:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**Instalar Redis**:
```bash
pip install django-redis redis
```

## Testing

### Probar rate limiting manualmente

```bash
# Hacer 6 solicitudes seguidas (exceder límite de 5/min)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"account_number":"1234567","password":"wrong"}' \
    && echo "Request $i"
done
```

### Desactivar en tests automatizados

```python
# En settings_test.py o conftest.py
RATELIMIT_ENABLE = False
```

## Recomendaciones de Seguridad

1. ✅ **Usar Redis en producción**: LocMemCache no funciona con múltiples workers
2. ✅ **Monitorear 429s**: Configurar alertas para excesos de 429
3. ✅ **Ajustar según uso real**: Los límites actuales son conservadores
4. ✅ **Combinar con firewall**: Rate limiting a nivel de aplicación + firewall
5. ✅ **Considerar IP ranges**: Si usas proxies/load balancers, configurar `X-Forwarded-For`

## Referencias

- [django-ratelimit Documentation](https://django-ratelimit.readthedocs.io/)
- [OWASP Rate Limiting](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)
- [HTTP 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)