# Sistema de Auditoría - MAC Attendance

## Resumen

El proyecto implementa un sistema completo de auditoría para:
- ✅ Registrar eventos de seguridad
- ✅ Rastrear acciones de usuarios
- ✅ Detectar comportamientos sospechosos
- ✅ Cumplir con requisitos de cumplimiento
- ✅ Facilitar investigaciones de seguridad

## Componentes del Sistema

### 1. Modelo AuditLog

**Ubicación**: `backend/authentication/audit.py`

Modelo de base de datos que almacena todos los eventos de auditoría.

**Campos principales**:
```python
- timestamp: Fecha y hora del evento
- category: Categoría (AUTH, ACCESS, DATA, SECURITY, SYSTEM)
- severity: Nivel (INFO, WARNING, ERROR, CRITICAL)
- action: Acción específica (LOGIN_SUCCESS, ACCESS_DENIED, etc.)
- user: Usuario relacionado (ForeignKey)
- username: Backup del nombre de usuario
- ip_address: Dirección IP del cliente
- user_agent: User agent del navegador
- path: Ruta de la solicitud
- method: Método HTTP (GET, POST, etc.)
- message: Mensaje descriptivo
- details: Datos adicionales en JSON
- success: Si la operación fue exitosa
- status_code: Código HTTP de respuesta
```

### 2. Categorías de Eventos

| Categoría | Descripción | Ejemplos |
|-----------|-------------|----------|
| **AUTH** | Autenticación | Login, logout, token refresh |
| **ACCESS** | Control de acceso | Permisos denegados, accesos no autorizados |
| **DATA** | Modificación de datos | Creación, actualización, eliminación |
| **SECURITY** | Eventos de seguridad | Rate limiting, intentos de ataque |
| **SYSTEM** | Eventos del sistema | Errores internos, mantenimiento |

### 3. Acciones Registradas

#### Autenticación
- `LOGIN_SUCCESS`: Login exitoso
- `LOGIN_FAILED`: Login fallido
- `LOGOUT`: Cierre de sesión
- `TOKEN_REFRESH`: Token JWT refrescado

#### Seguridad
- `ACCESS_DENIED`: Acceso denegado (401, 403)
- `RATE_LIMITED`: Rate limit excedido (429)

#### Datos
- `ATTENDANCE_CREATE`: Asistencia registrada
- `ATTENDANCE_UPDATE`: Asistencia actualizada
- `ATTENDANCE_DELETE`: Asistencia eliminada
- `EVENT_CREATE`: Evento creado
- `EVENT_UPDATE`: Evento actualizado
- `EVENT_DELETE`: Evento eliminado
- `EXTERNAL_USER_REGISTER`: Usuario externo registrado
- `EXTERNAL_USER_APPROVE`: Usuario externo aprobado
- `EXTERNAL_USER_REJECT`: Usuario externo rechazado

## Uso del Sistema

### Registrar un Evento Manualmente

```python
from authentication.audit import AuditLog

# En cualquier vista
AuditLog.log(
    category='DATA',
    action='ATTENDANCE_CREATE',
    message='Asistencia registrada para estudiante 1234567',
    request=request,
    user=request.user,
    severity='INFO',
    success=True,
    status_code=201,
    student_account='1234567',
    event_id=event.id
)
```

### Eventos Automáticos

El middleware `AuditMiddleware` registra automáticamente:

**401 Unauthorized**:
```
[WARNING] Intento de acceso no autorizado a /api/attendance/register/
```

**403 Forbidden**:
```
[WARNING] Acceso denegado (permisos insuficientes) a /api/events/approve/5/
```

**429 Too Many Requests**:
```
[WARNING] Rate limit excedido para /api/auth/login/
```

### Consultar Logs de Auditoría

#### Desde Django Admin
1. Ir a `/admin/authentication/auditlog/`
2. Filtrar por categoría, severidad, acción, éxito
3. Buscar por usuario, IP, mensaje
4. Ver detalles completos en JSON

#### Desde Python/Django Shell

```python
from authentication.audit import AuditLog

# Ver últimos 10 eventos
AuditLog.objects.all()[:10]

# Intentos fallidos de login en las últimas 24 horas
AuditLog.get_failed_logins(hours=24)

# Actividad de un usuario específico (últimos 30 días)
AuditLog.get_user_activity(user=my_user, days=30)

# Eventos de seguridad críticos
AuditLog.get_security_events(severity='CRITICAL', hours=24)

# Filtrar por IP
AuditLog.objects.filter(ip_address='192.168.1.100')

# Eventos de una categoría específica
AuditLog.objects.filter(category='AUTH')

# Acciones fallidas
AuditLog.objects.filter(success=False)
```

## Archivos de Log

El sistema mantiene 3 archivos de log separados:

### 1. `backend/logs/django.log`
- Logs generales de Django
- Nivel: INFO (producción) / DEBUG (desarrollo)
- Uso: Debugging general

### 2. `backend/logs/security.log`
- Eventos de seguridad específicos
- Nivel: WARNING+
- Uso: Monitoreo de seguridad

### 3. `backend/logs/audit.log`
- Registros de auditoría
- Nivel: INFO+
- Uso: Trazabilidad y cumplimiento

**Formato de logs**:
```
[AUDIT] 2025-09-30 12:34:56 INFO Login exitoso para cuenta 1234567
[AUDIT] 2025-09-30 12:35:10 WARNING Intento de login fallido para cuenta 9999999
```

## Seguridad y Privacidad

### Datos Sensibles Sanitizados

El sistema **NO guarda** información sensible:
- ❌ Contraseñas (redactadas automáticamente)
- ❌ Tokens completos (redactados)
- ❌ Claves secretas (redactadas)
- ✅ Solo datos necesarios para auditoría

**Ejemplo**:
```python
# Entrada
details = {
    'password': 'mi_contraseña_secreta',
    'token': 'eyJhbGciOiJIUzI1...',
    'account': '1234567'
}

# Almacenado
{
    'password': '***REDACTED***',
    'token': '***REDACTED***',
    'account': '1234567'
}
```

### Inmutabilidad de Logs

Los logs de auditoría son **inmutables**:
- ❌ No se pueden crear manualmente desde admin
- ❌ No se pueden editar
- ✅ Solo superusuarios pueden eliminar (casos extremos)

## Consultas Útiles

### Detectar Intentos de Ataque

```python
# IPs con más de 10 intentos fallidos de login en 1 hora
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

cutoff = timezone.now() - timedelta(hours=1)
suspicious_ips = (
    AuditLog.objects
    .filter(action='LOGIN_FAILED', timestamp__gte=cutoff)
    .values('ip_address')
    .annotate(attempts=Count('id'))
    .filter(attempts__gt=10)
    .order_by('-attempts')
)
```

### Actividad Inusual de un Usuario

```python
# Accesos desde diferentes IPs en poco tiempo
user_logs = AuditLog.objects.filter(
    user=my_user,
    timestamp__gte=timezone.now() - timedelta(hours=1)
).values('ip_address').distinct()

if user_logs.count() > 3:
    print("⚠️ Usuario accediendo desde múltiples IPs")
```

### Exportar Logs para Análisis

```python
import json

# Exportar a JSON
logs = AuditLog.objects.filter(
    timestamp__gte=timezone.now() - timedelta(days=7)
).values()

with open('audit_export.json', 'w') as f:
    json.dump(list(logs), f, default=str, indent=2)
```

## Monitoreo en Producción

### Alertas Recomendadas

Configurar alertas para:

1. **Múltiples intentos fallidos de login**
   - Umbral: 5+ intentos en 5 minutos desde una IP
   - Acción: Bloqueo temporal de IP

2. **Accesos denegados repetidos**
   - Umbral: 10+ eventos 403/401 en 10 minutos
   - Acción: Revisar configuración de permisos

3. **Rate limiting frecuente**
   - Umbral: 100+ eventos 429 en 1 hora
   - Acción: Revisar límites o investigar ataque

4. **Eventos CRITICAL**
   - Cualquier evento con severity='CRITICAL'
   - Acción: Notificación inmediata

### Script de Monitoreo Ejemplo

```python
# monitor_audit.py
from authentication.audit import AuditLog
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail

def check_security_alerts():
    """Verificar y enviar alertas de seguridad"""
    cutoff = timezone.now() - timedelta(minutes=5)

    # Verificar intentos fallidos
    failed_logins = AuditLog.objects.filter(
        action='LOGIN_FAILED',
        timestamp__gte=cutoff
    ).count()

    if failed_logins > 10:
        send_mail(
            'Alerta de Seguridad: Múltiples intentos fallidos',
            f'Se detectaron {failed_logins} intentos fallidos de login en los últimos 5 minutos',
            'noreply@mac-attendance.com',
            ['admin@mac-attendance.com'],
        )

# Ejecutar con cron cada 5 minutos
# */5 * * * * cd /path/to/project && python manage.py shell < monitor_audit.py
```

## Retención de Logs

### Configuración Recomendada

- **Desarrollo**: 30 días
- **Producción**: 1-2 años (dependiendo de requisitos legales)

### Script de Limpieza

```python
# cleanup_old_logs.py
from authentication.audit import AuditLog
from datetime import timedelta
from django.utils import timezone

def cleanup_old_audit_logs(days=365):
    """Eliminar logs más antiguos que N días"""
    cutoff = timezone.now() - timedelta(days=days)
    deleted_count = AuditLog.objects.filter(timestamp__lt=cutoff).delete()[0]

    print(f"Eliminados {deleted_count} registros antiguos")

# Ejecutar mensualmente con cron
# 0 2 1 * * cd /path/to/project && python manage.py shell < cleanup_old_logs.py
```

## Extensiones Futuras

### Integraciones Posibles

1. **SIEM (Security Information and Event Management)**
   - Splunk
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Graylog

2. **Servicios de Alertas**
   - Sentry para errores
   - PagerDuty para alertas críticas
   - Slack/Discord para notificaciones

3. **Análisis de Comportamiento**
   - Machine Learning para detectar anomalías
   - Patrones de uso inusuales
   - Identificación de cuentas comprometidas

## Buenas Prácticas

### ✅ DO

- Registrar todos los eventos de seguridad
- Incluir contexto suficiente (IP, user agent, timestamp)
- Usar niveles de severidad apropiados
- Revisar logs regularmente
- Configurar alertas para eventos críticos
- Mantener logs por períodos apropiados

### ❌ DON'T

- Guardar contraseñas o tokens en logs
- Registrar datos personales sensibles innecesarios
- Ignorar eventos WARNING o ERROR
- Permitir que usuarios normales editen logs
- Olvidar limpieza periódica de logs antiguos

## Referencias

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [NIST SP 800-92: Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [CIS Controls: Log Management](https://www.cisecurity.org/controls/)