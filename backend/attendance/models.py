from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time as dt_time, timedelta
from authentication.models import UserProfile, ExternalUser
from events.models import Event

class Attendance(models.Model):
    REGISTRATION_METHODS = (
        ('manual', 'Registro Manual'),
        ('barcode', 'Código de Barras'),
        ('external', 'Usuario Externo'),
    )
    
    # Puede ser estudiante regular o externo
    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to={'user_type': 'student'},
        verbose_name="Estudiante"
    )
    external_user = models.ForeignKey(
        ExternalUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Usuario Externo"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Evento"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Hora de registro"
    )
    registered_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='registered_attendances',
        limit_choices_to={'user_type': 'assistant'},
        verbose_name="Registrado por"
    )
    registration_method = models.CharField(
        max_length=10,
        choices=REGISTRATION_METHODS,
        default='manual',
        verbose_name="Método de registro"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas adicionales"
    )
    is_valid = models.BooleanField(
        default=True,
        verbose_name="Asistencia válida"
    )
    
    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ['-timestamp']
    
    def clean(self):
        # Debe tener estudiante O usuario externo, pero no ambos
        if not self.student and not self.external_user:
            raise ValidationError("Debe especificar un estudiante o usuario externo.")

        if self.student and self.external_user:
            raise ValidationError("No puede tener ambos: estudiante y usuario externo.")

        # Validar que el registrador sea un asistente
        if self.registered_by.user_type != 'assistant':
            raise ValidationError("Solo los asistentes pueden registrar asistencias.")

        # Validar que el evento esté en curso (entre start_time y end_time)
        now = timezone.now()
        event_date = self.event.date
        event_start = datetime.combine(event_date, self.event.start_time)
        event_end = datetime.combine(event_date, self.event.end_time)

        # Hacer timezone-aware si es necesario
        if timezone.is_naive(event_start):
            event_start = timezone.make_aware(event_start)
        if timezone.is_naive(event_end):
            event_end = timezone.make_aware(event_end)

        # Permitir registro desde 10 minutos antes hasta el final del evento
        registration_start = event_start - timedelta(minutes=10)

        if now < registration_start:
            raise ValidationError(
                f"No se puede registrar asistencia antes del evento. "
                f"El evento inicia el {event_date.strftime('%d/%m/%Y')} a las {self.event.start_time.strftime('%H:%M')}. "
                f"Puedes registrar desde 10 minutos antes."
            )

        if now > event_end:
            raise ValidationError(
                f"No se puede registrar asistencia después del evento. "
                f"El evento terminó el {event_date.strftime('%d/%m/%Y')} a las {self.event.end_time.strftime('%H:%M')}."
            )

        # Validar que no haya duplicados
        if self.student:
            existing = Attendance.objects.filter(
                student=self.student,
                event=self.event,
                is_valid=True
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Este estudiante ya tiene asistencia registrada para este evento.")
        
        if self.external_user:
            existing = Attendance.objects.filter(
                external_user=self.external_user,
                event=self.event,
                is_valid=True
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Este usuario externo ya tiene asistencia registrada para este evento.")
        
        # Validar eventos simultáneos (solo para estudiantes regulares)
        if self.student:
            overlapping_events = Event.objects.filter(
                date=self.event.date,
                start_time__lt=self.event.end_time,
                end_time__gt=self.event.start_time,
                is_active=True
            ).exclude(id=self.event.id)
            
            existing_attendance = Attendance.objects.filter(
                student=self.student,
                event__in=overlapping_events,
                is_valid=True
            ).exists()
            
            if existing_attendance:
                raise ValidationError(
                    "El estudiante ya tiene asistencia registrada en un evento simultáneo."
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # Actualizar estadísticas si es estudiante regular
        if self.student:
            self.update_student_stats()
    
    def update_student_stats(self):
        """Actualizar las estadísticas de asistencia del estudiante"""
        stats, created = AttendanceStats.objects.get_or_create(
            student=self.student,
            defaults={
                'total_events': 0,
                'attended_events': 0,
                'attendance_percentage': 0.0
            }
        )
        stats.update_stats()
    
    @property
    def attendee_name(self):
        """Nombre del asistente (estudiante o externo)"""
        if self.student:
            return self.student.full_name
        elif self.external_user:
            return self.external_user.full_name
        return "Desconocido"
    
    @property
    def attendee_identifier(self):
        """Identificador del asistente"""
        if self.student:
            return self.student.account_number
        elif self.external_user:
            return self.external_user.account_number
        return "N/A"
    
    def __str__(self):
        return f"{self.attendee_name} - {self.event.title}"

class AttendanceStats(models.Model):
    student = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'student'},
        verbose_name="Estudiante"
    )
    total_events = models.IntegerField(
        default=0,
        verbose_name="Total de eventos"
    )
    attended_events = models.IntegerField(
        default=0,
        verbose_name="Eventos asistidos"
    )
    attendance_percentage = models.FloatField(
        default=0.0,
        verbose_name="Porcentaje de asistencia"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    class Meta:
        verbose_name = "Estadísticas de asistencia"
        verbose_name_plural = "Estadísticas de asistencia"
    
    def update_stats(self):
        """Actualizar las estadísticas de asistencia"""
        from events.models import Event  # Importar aquí para evitar circular imports
        
        # Contar TODOS los eventos activos
        total = Event.objects.filter(is_active=True).count()
        
        # Contar asistencias válidas del estudiante
        attended = Attendance.objects.filter(
            student=self.student,
            is_valid=True
        ).count()
        
        self.total_events = total
        self.attended_events = attended
        
        # Calcular porcentaje
        if total > 0:
            self.attendance_percentage = round((attended / total) * 100, 2)
        else:
            self.attendance_percentage = 0.0
        
        self.save()
    
    def meets_minimum_requirement(self):
        """Verifica si cumple con el requisito mínimo de asistencia global"""
        from authentication.models import SystemConfiguration
        config = SystemConfiguration.get_config()
        return self.attendance_percentage >= config.minimum_attendance_percentage
    
    def __str__(self):
        return f"Stats: {self.student.full_name} - {self.attendance_percentage}%"