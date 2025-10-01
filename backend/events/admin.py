from django.contrib import admin
from django.utils.html import format_html
from .models import Event, ExternalUser

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'speaker', 'date', 'start_time', 'modality', 'location', 'is_active', 'get_created_by']
    list_filter = ['event_type', 'modality', 'date', 'is_active', 'created_by']
    search_fields = ['title', 'speaker', 'location', 'created_by__full_name']
    date_hierarchy = 'date'
    ordering = ['date', 'start_time']
    readonly_fields = ['created_at']

    def get_created_by(self, obj):
        """Muestra quién creó el evento"""
        if obj.created_by:
            return format_html(
                '<span style="color: #0066cc;">👤 {}</span>',
                obj.created_by.full_name
            )
        return '-'
    get_created_by.short_description = 'Creado por'

@admin.register(ExternalUser)
class ExternalUserAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'full_name', 'get_status', 'get_approved_by', 'created_at']
    list_filter = ['status', 'created_at', 'approved_by']
    search_fields = ['full_name', 'account_number', 'approved_by__full_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'processed_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información Personal', {
            'fields': ('account_number', 'full_name')
        }),
        ('Estado de Aprobación', {
            'fields': ('status', 'approved_by', 'processed_at', 'rejection_reason', 'created_at')
        }),
    )

    def get_status(self, obj):
        """Muestra el estado con iconos y colores"""
        status_icons = {
            'pending': ('⏳', '#FFA500', 'Pendiente'),
            'approved': ('✅', '#28a745', 'Aprobado'),
            'rejected': ('❌', '#dc3545', 'Rechazado')
        }
        icon, color, text = status_icons.get(obj.status, ('?', '#666', obj.status))
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, text
        )
    get_status.short_description = 'Estado'

    def get_approved_by(self, obj):
        """Muestra quién aprobó/rechazó al usuario"""
        if obj.approved_by:
            color = '#28a745' if obj.status == 'approved' else '#dc3545'
            action = 'Aprobado por' if obj.status == 'approved' else 'Rechazado por'
            return format_html(
                '<span style="color: {};">👤 {}</span><br><small>{}</small>',
                color,
                obj.approved_by.full_name,
                action
            )
        return '-'
    get_approved_by.short_description = 'Procesado por'