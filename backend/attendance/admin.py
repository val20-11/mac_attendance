from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse
from import_export import resources, fields
from import_export.admin import ExportMixin
from .models import Attendance, AttendanceStats


class AttendanceStatsResource(resources.ModelResource):
    """Recurso para exportar estadísticas de asistencia"""
    account_number = fields.Field()
    full_name = fields.Field()
    cumple_requisito = fields.Field()

    class Meta:
        model = AttendanceStats
        fields = ('account_number', 'full_name', 'attended_events', 'total_events',
                  'attendance_percentage', 'cumple_requisito')
        export_order = fields

    def dehydrate_account_number(self, stats):
        """Obtener número de cuenta del estudiante"""
        return stats.student.account_number

    def dehydrate_full_name(self, stats):
        """Obtener nombre completo del estudiante"""
        return stats.student.full_name

    def dehydrate_cumple_requisito(self, stats):
        """Verificar si cumple el requisito mínimo"""
        return 'SÍ' if stats.meets_minimum_requirement() else 'NO'

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

    def has_change_permission(self, request, obj=None):
        # Solo superusuarios pueden editar asistencias (para correcciones excepcionales)
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar asistencias
        return request.user.is_superuser

@admin.register(AttendanceStats)
class AttendanceStatsAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AttendanceStatsResource
    list_display = ['student', 'attended_events', 'total_events', 'attendance_percentage', 'get_cumple_requisito']
    ordering = ['-attendance_percentage']
    list_filter = ['attendance_percentage']
    search_fields = ['student__account_number', 'student__full_name']
    actions = ['export_selected_stats', 'export_students_with_certificate']

    def get_cumple_requisito(self, obj):
        """Mostrar si cumple el requisito mínimo"""
        cumple = obj.meets_minimum_requirement()
        color = '#28a745' if cumple else '#dc3545'
        text = '✅ SÍ' if cumple else '❌ NO'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    get_cumple_requisito.short_description = 'Cumple requisito'

    def export_selected_stats(self, request, queryset):
        """Acción para exportar estadísticas seleccionadas"""
        resource = AttendanceStatsResource()
        dataset = resource.export(queryset)

        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="estadisticas_asistencia.xlsx"'

        self.message_user(request, f'Se exportaron {queryset.count()} estadísticas.')
        return response

    export_selected_stats.short_description = "📊 Exportar estadísticas seleccionadas"

    def export_students_with_certificate(self, request, queryset):
        """Acción para exportar solo estudiantes que cumplen el requisito mínimo"""
        from authentication.models import SystemConfiguration
        config = SystemConfiguration.get_config()

        # Filtrar solo los que cumplen el requisito
        qualified_students = queryset.filter(
            attendance_percentage__gte=config.minimum_attendance_percentage
        )

        # Crear el recurso y exportar
        resource = AttendanceStatsResource()
        dataset = resource.export(qualified_students)

        # Generar archivo Excel
        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="estudiantes_con_constancia.xlsx"'

        self.message_user(
            request,
            f'Se exportaron {qualified_students.count()} estudiantes que cumplen con el {config.minimum_attendance_percentage}% de asistencia mínima.'
        )

        return response

    export_students_with_certificate.short_description = "📊 Exportar estudiantes que cumplen requisito para constancia"

    def get_export_formats(self):
        """Formatos permitidos para exportar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def has_add_permission(self, request):
        # Las estadísticas se generan automáticamente
        return False

    def has_change_permission(self, request, obj=None):
        # Las estadísticas son de solo lectura
        return False

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar estadísticas
        return request.user.is_superuser