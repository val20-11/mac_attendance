from django.contrib import admin
from django.utils.html import format_html
from .models import Attendance, AttendanceStats

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['attendee_name', 'attendee_identifier', 'event', 'timestamp', 'registration_method', 'get_registered_by', 'is_valid']
    list_filter = ['registration_method', 'registered_by', 'event__date', 'is_valid', 'event']
    search_fields = ['student__full_name', 'student__account_number', 'external_user__full_name',
                     'external_user__temporary_id', 'event__title', 'registered_by__full_name',
                     'registered_by__account_number']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp', 'attendee_name', 'attendee_identifier']
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Información del Asistente', {
            'fields': ('student', 'external_user', 'attendee_name', 'attendee_identifier')
        }),
        ('Información del Evento', {
            'fields': ('event',)
        }),
        ('Registro', {
            'fields': ('registered_by', 'registration_method', 'timestamp', 'is_valid', 'notes')
        }),
    )

    def get_registered_by(self, obj):
        """Muestra el asistente que registró con formato mejorado"""
        if obj.registered_by:
            return format_html(
                '<span style="color: #0066cc;">👤 {}</span><br><small>Cuenta: {}</small>',
                obj.registered_by.full_name,
                obj.registered_by.account_number
            )
        return '-'
    get_registered_by.short_description = 'Registrado por'

    def has_add_permission(self, request):
        # Prevenir creación manual desde admin (debe hacerse desde la API)
        return False

@admin.register(AttendanceStats)
class AttendanceStatsAdmin(admin.ModelAdmin):
    list_display = ['student', 'attended_events', 'total_events', 'attendance_percentage']
    ordering = ['-attendance_percentage']