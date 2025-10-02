from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

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
        verbose_name="Tipo de usuario"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="Nombre completo"
    )

    def __str__(self):
        return f"{self.account_number} - {self.full_name}"

class Asistente(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    minimum_attendance_percentage = models.FloatField(default=80.0)
    can_manage_events = models.BooleanField(default=True)

    def __str__(self):
        return f"Asistente: {self.user_profile.full_name}"

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