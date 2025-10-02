from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from authentication.models import UserProfile

class Event(models.Model):
    EVENT_TYPES = (
        ('conference', 'Conferencia'),
        ('workshop', 'Taller'),
        ('panel', 'Mesa Redonda'),
        ('seminar', 'Seminario'),
    )
    
    MODALITY_CHOICES = (
        ('presencial', 'Presencial'),
        ('online', 'En línea'),
        ('hybrid', 'Híbrido'),
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título de la ponencia"
    )
    description = models.TextField(
        verbose_name="Descripción"
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        default='conference',
        verbose_name="Tipo de evento"
    )
    modality = models.CharField(
        max_length=15,
        choices=MODALITY_CHOICES,
        default='presencial',
        verbose_name="Modalidad"
    )
    speaker = models.CharField(
        max_length=200,
        verbose_name="Ponente"
    )
    date = models.DateField(verbose_name="Fecha")
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de fin")
    location = models.CharField(
        max_length=200,
        verbose_name="Ubicación/Plataforma",
        help_text="Para eventos presenciales: aula/salón. Para eventos en línea: enlace o plataforma"
    )
    max_capacity = models.IntegerField(
        default=100,
        verbose_name="Capacidad máxima"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Evento activo"
    )
    requires_registration = models.BooleanField(
        default=False,
        verbose_name="Requiere registro previo"
    )
    meeting_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Enlace de reunión",
        help_text="Para eventos en línea o híbridos"
    )
    meeting_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="ID de reunión",
        help_text="Código de sala/reunión"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'authentication.UserProfile',
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'assistant'},
        verbose_name="Creado por"
    )
    
    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = "Evento/Ponencia"
        verbose_name_plural = "Eventos/Ponencias"
    
    def clean(self):
        # Validar que la hora de fin sea después de la hora de inicio
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        
        # Validar que la fecha/hora del evento no haya terminado
        if self.date and self.end_time:
            from datetime import datetime
            event_end = datetime.combine(self.date, self.end_time)

            # Hacer timezone-aware si es necesario
            if timezone.is_naive(event_end):
                event_end = timezone.make_aware(event_end)

            # Solo validar si el evento ya terminó completamente
            if event_end < timezone.now():
                raise ValidationError("No se puede crear un evento que ya finalizó.")
        
        # Validar que eventos en línea tengan enlace
        if self.modality in ['online', 'hybrid'] and not self.meeting_link:
            raise ValidationError("Los eventos en línea o híbridos requieren un enlace de reunión.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def duration_minutes(self):
        """Duración del evento en minutos"""
        if self.start_time and self.end_time:
            start_datetime = timezone.datetime.combine(self.date, self.start_time)
            end_datetime = timezone.datetime.combine(self.date, self.end_time)
            duration = end_datetime - start_datetime
            return duration.total_seconds() / 60
        return 0
    
    @property
    def is_happening_now(self):
        """Verifica si el evento está ocurriendo ahora"""
        now = timezone.now()
        if self.date == now.date():
            current_time = now.time()
            return self.start_time <= current_time <= self.end_time
        return False
    
    @property
    def is_online(self):
        """Verifica si el evento es en línea"""
        return self.modality in ['online', 'hybrid']
    
    def __str__(self):
        modality_icon = "🖥️" if self.is_online else "🏢"
        return f"{modality_icon} {self.title} - {self.date} {self.start_time}"