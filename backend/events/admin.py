from django.contrib import admin
from django.utils.html import format_html
from .models import Event

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