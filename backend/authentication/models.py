from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    USER_TYPES = (
        ('student', 'Estudiante'),
        ('assistant', 'Asistente'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(
        max_length=7,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{7}$',
            message='El número de cuenta debe tener exactamente 7 dígitos.'
        )],
        verbose_name="Número de cuenta"
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPES,
        blank=False,
        null=False,
        verbose_name="Tipo de usuario"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="Nombre completo"
    )

    def __str__(self):
        return f"{self.account_number} - {self.full_name}"

class Asistente(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, limit_choices_to={'user_type': 'assistant'})
    can_manage_events = models.BooleanField(default=True, verbose_name="Puede gestionar eventos")

    class Meta:
        verbose_name = "Permiso de Asistente"
        verbose_name_plural = "Permisos de Asistentes"

    def clean(self):
        """Validar que el user_profile sea de tipo assistant"""
        from django.core.exceptions import ValidationError
        if self.user_profile and self.user_profile.user_type != 'assistant':
            raise ValidationError({
                'user_profile': 'Solo se pueden asignar permisos a usuarios de tipo Asistente. Este usuario es un Estudiante.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Permisos: {self.user_profile.full_name}"

class ExternalUser(models.Model):
    """Usuarios externos"""
    APPROVAL_STATUS = (
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    )

    full_name = models.CharField(max_length=200, verbose_name="Nombre completo")
    account_number = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Número de cuenta"
    )
    status = models.CharField(
        max_length=10,
        choices=APPROVAL_STATUS,
        default='approved',
        verbose_name="Estado de aprobación"
    )
    approved_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Aprobado por"
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo de rechazo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Usuario Externo"
        verbose_name_plural = "Usuarios Externos"
        ordering = ['-created_at']

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_pending(self):
        return self.status == 'pending'

    def approve(self, approved_by_user):
        """Aprobar usuario externo"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.processed_at = timezone.now()
        self.save()

    def reject(self, rejected_by_user, reason=""):
        """Rechazar usuario externo"""
        self.status = 'rejected'
        self.approved_by = rejected_by_user
        self.rejection_reason = reason
        self.processed_at = timezone.now()
        self.save()

    def __str__(self):
        status_icons = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌'
        }
        icon = status_icons.get(self.status, '?')
        return f"{icon} {self.full_name} - {self.account_number}"


class SystemConfiguration(models.Model):
    """Configuración global del sistema"""
    minimum_attendance_percentage = models.FloatField(
        default=80.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Porcentaje mínimo de asistencia",
        help_text="Porcentaje mínimo de asistencia requerido para obtener constancia (0-100)"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    updated_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Actualizado por"
    )

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"

    def save(self, *args, **kwargs):
        # Asegurar que solo exista una instancia de configuración
        if not self.pk and SystemConfiguration.objects.exists():
            raise ValidationError("Solo puede existir una configuración del sistema.")
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Obtener o crear la configuración del sistema"""
        config, created = cls.objects.get_or_create(
            pk=1,
            defaults={'minimum_attendance_percentage': 80.0}
        )
        return config

    def __str__(self):
        return f"Configuración del Sistema - Asistencia mínima: {self.minimum_attendance_percentage}%"


# ===== PROXY MODELS PARA SEPARAR ESTUDIANTES Y ASISTENTES EN EL ADMIN =====

class Student(UserProfile):
    """Proxy model para estudiantes"""
    class Meta:
        proxy = True
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def save(self, *args, **kwargs):
        self.user_type = 'student'
        super().save(*args, **kwargs)


class AssistantProfile(UserProfile):
    """Proxy model para asistentes"""
    class Meta:
        proxy = True
        verbose_name = "Asistente (Perfil)"
        verbose_name_plural = "Asistentes (Perfiles)"

    def save(self, *args, **kwargs):
        self.user_type = 'assistant'
        super().save(*args, **kwargs)