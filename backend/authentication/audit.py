"""
Sistema de auditoría para registrar eventos de seguridad
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Modelo para registrar eventos de auditoría del sistema
    """

    # Categorías de eventos
    CATEGORY_CHOICES = [
        ('AUTH', 'Autenticación'),
        ('ACCESS', 'Control de Acceso'),
        ('DATA', 'Modificación de Datos'),
        ('SECURITY', 'Evento de Seguridad'),
        ('SYSTEM', 'Sistema'),
    ]

    # Niveles de severidad
    SEVERITY_CHOICES = [
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Crítico'),
    ]

    # Acciones comunes
    ACTION_CHOICES = [
        ('LOGIN_SUCCESS', 'Login exitoso'),
        ('LOGIN_FAILED', 'Login fallido'),
        ('LOGOUT', 'Logout'),
        ('TOKEN_REFRESH', 'Token refrescado'),
        ('ACCESS_DENIED', 'Acceso denegado'),
        ('RATE_LIMITED', 'Rate limit excedido'),
        ('ATTENDANCE_CREATE', 'Asistencia registrada'),
        ('ATTENDANCE_UPDATE', 'Asistencia actualizada'),
        ('ATTENDANCE_DELETE', 'Asistencia eliminada'),
        ('EVENT_CREATE', 'Evento creado'),
        ('EVENT_UPDATE', 'Evento actualizado'),
        ('EVENT_DELETE', 'Evento eliminado'),
        ('EXTERNAL_USER_REGISTER', 'Usuario externo registrado'),
        ('EXTERNAL_USER_APPROVE', 'Usuario externo aprobado'),
        ('EXTERNAL_USER_REJECT', 'Usuario externo rechazado'),
        ('PERMISSION_CHANGE', 'Cambio de permisos'),
        ('DATA_EXPORT', 'Exportación de datos'),
        ('OTHER', 'Otro'),
    ]

    # Campos principales
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='INFO', db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    # Usuario relacionado (puede ser None para eventos anónimos)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    username = models.CharField(max_length=150, blank=True)  # Backup si el usuario se elimina

    # Información de la solicitud
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=10, blank=True)

    # Detalles del evento
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)  # Datos adicionales en JSON

    # Resultados
    success = models.BooleanField(default=True)
    status_code = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'category']),
            models.Index(fields=['-timestamp', 'severity']),
            models.Index(fields=['-timestamp', 'user']),
            models.Index(fields=['ip_address', '-timestamp']),
        ]
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'

    def __str__(self):
        return f"[{self.timestamp}] {self.get_category_display()} - {self.message}"

    @classmethod
    def log(cls, category, action, message, request=None, user=None,
            severity='INFO', success=True, status_code=None, **details):
        """
        Método de conveniencia para crear logs de auditoría

        Args:
            category: Categoría del evento
            action: Acción realizada
            message: Mensaje descriptivo
            request: Objeto request de Django (opcional)
            user: Usuario (opcional, se extrae del request si no se provee)
            severity: Nivel de severidad
            success: Si la operación fue exitosa
            status_code: Código HTTP de respuesta
            **details: Datos adicionales a guardar en JSON
        """
        # Extraer información del request
        ip_address = None
        user_agent = ''
        path = ''
        method = ''

        if request:
            # Obtener IP real (considerando proxies)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar tamaño
            path = request.path
            method = request.method

            # Si no se proveyó usuario, intentar obtenerlo del request
            if not user and hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user

        # Obtener username
        username = user.username if user else 'Anonymous'

        # Sanitizar detalles (no guardar datos sensibles)
        sanitized_details = cls._sanitize_details(details)

        # Crear el log
        return cls.objects.create(
            category=category,
            severity=severity,
            action=action,
            user=user,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            path=path,
            method=method,
            message=message,
            details=sanitized_details,
            success=success,
            status_code=status_code,
        )

    @staticmethod
    def _sanitize_details(details):
        """
        Eliminar datos sensibles de los detalles antes de guardar
        """
        sensitive_keys = ['password', 'token', 'secret', 'key', 'authorization']
        sanitized = {}

        for key, value in details.items():
            # Verificar si la clave contiene información sensible
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                sanitized[key] = AuditLog._sanitize_details(value)
            else:
                # Limitar tamaño de strings
                if isinstance(value, str) and len(value) > 1000:
                    sanitized[key] = value[:1000] + '...[truncated]'
                else:
                    sanitized[key] = value

        return sanitized

    @classmethod
    def get_user_activity(cls, user, days=30):
        """
        Obtener actividad de un usuario en los últimos N días
        """
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(user=user, timestamp__gte=cutoff)

    @classmethod
    def get_failed_logins(cls, ip_address=None, hours=24):
        """
        Obtener intentos fallidos de login
        """
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(hours=hours)

        query = cls.objects.filter(
            action='LOGIN_FAILED',
            timestamp__gte=cutoff
        )

        if ip_address:
            query = query.filter(ip_address=ip_address)

        return query

    @classmethod
    def get_security_events(cls, severity='WARNING', hours=24):
        """
        Obtener eventos de seguridad recientes
        """
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(hours=hours)

        return cls.objects.filter(
            category='SECURITY',
            severity__in=[severity, 'ERROR', 'CRITICAL'],
            timestamp__gte=cutoff
        )