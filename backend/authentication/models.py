from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator

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
    career = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Carrera"
    )
    semester = models.IntegerField(
        blank=True, 
        null=True,
        verbose_name="Semestre"
    )

    def __str__(self):
        return f"{self.account_number} - {self.full_name}"

class Asistente(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    minimum_attendance_percentage = models.FloatField(default=80.0)
    can_manage_events = models.BooleanField(default=True)

    def __str__(self):
        return f"Asistente: {self.user_profile.full_name}"