from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile, Asistente
from .audit import AuditLog


class UserProfileForm(forms.ModelForm):
    """Formulario personalizado para crear UserProfile sin contraseña"""

    class Meta:
        model = UserProfile
        fields = ['account_number', 'full_name', 'user_type']

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Si el perfil no tiene usuario asociado, crear uno automáticamente
        if not profile.user_id:
            # Crear usuario con username = número de cuenta, sin contraseña
            user = User.objects.create_user(
                username=profile.account_number,
                first_name=profile.full_name,
                password=None  # Sin contraseña
            )
            # Desactivar contraseña usable
            user.set_unusable_password()
            user.save()
            profile.user = user

        if commit:
            profile.save()

        return profile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm
    list_display = ['account_number', 'full_name', 'user_type']
    search_fields = ['account_number', 'full_name']
    list_filter = ['user_type']

    fieldsets = (
        ('Información del Usuario', {
            'fields': ('account_number', 'full_name', 'user_type'),
            'description': 'Los usuarios se crean automáticamente sin contraseña. El acceso es solo con número de cuenta.'
        }),
    )


@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'get_registros_realizados', 'ver_alumnos_registrados', 'minimum_attendance_percentage', 'can_manage_events']
    list_filter = ['can_manage_events']
    search_fields = ['user_profile__full_name', 'user_profile__account_number']
    readonly_fields = ['get_registros_realizados', 'get_ultimos_registros']
    actions = ['ver_reporte_registros']

    fieldsets = (
        ('Información del Asistente', {
            'fields': ('user_profile',)
        }),
        ('Permisos y Configuración', {
            'fields': ('can_manage_events', 'minimum_attendance_percentage')
        }),
        ('Estadísticas de Registros', {
            'fields': ('get_registros_realizados', 'get_ultimos_registros'),
            'classes': ('collapse',)
        }),
    )

    def get_registros_realizados(self, obj):
        """Muestra el total de registros realizados por este asistente"""
        from attendance.models import Attendance
        count = Attendance.objects.filter(registered_by=obj.user_profile).count()
        return f"📊 {count} registros"
    get_registros_realizados.short_description = 'Total de registros'

    def get_ultimos_registros(self, obj):
        """Muestra los últimos 5 registros realizados por este asistente"""
        from django.utils.html import format_html
        from attendance.models import Attendance

        registros = Attendance.objects.filter(
            registered_by=obj.user_profile
        ).select_related('student', 'external_user', 'event').order_by('-timestamp')[:5]

        if not registros:
            return "Sin registros"

        html = '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f0f0f0;"><th>Fecha</th><th>Asistente</th><th>Evento</th></tr>'

        for reg in registros:
            attendee = reg.student.full_name if reg.student else reg.external_user.full_name
            html += f'''
            <tr style="border-bottom: 1px solid #ddd;">
                <td>{reg.timestamp.strftime("%d/%m/%Y %H:%M")}</td>
                <td>{attendee}</td>
                <td>{reg.event.title[:30]}...</td>
            </tr>
            '''

        html += '</table>'
        return format_html(html)
    get_ultimos_registros.short_description = 'Últimos 5 registros'

    def ver_alumnos_registrados(self, obj):
        """Botón para ver todos los alumnos registrados por este asistente"""
        from django.utils.html import format_html
        from django.urls import reverse

        url = reverse('admin:attendance_attendance_changelist') + f'?registered_by__id__exact={obj.user_profile.id}'
        return format_html(
            '<a class="button" href="{}" style="background-color: #417690; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">📋 Ver Alumnos</a>',
            url
        )
    ver_alumnos_registrados.short_description = 'Alumnos Registrados'

    def ver_reporte_registros(self, request, queryset):
        """Acción para ver reporte detallado de registros de asistentes seleccionados"""
        from django.shortcuts import render
        from attendance.models import Attendance
        from django.db.models import Count, Q

        asistentes_data = []

        for asistente in queryset:
            registros = Attendance.objects.filter(registered_by=asistente.user_profile)

            estudiantes = registros.filter(student__isnull=False).select_related('student', 'event').order_by('-timestamp')
            externos = registros.filter(external_user__isnull=False).select_related('external_user', 'event').order_by('-timestamp')

            asistentes_data.append({
                'asistente': asistente,
                'total': registros.count(),
                'estudiantes': estudiantes,
                'externos': externos,
                'total_estudiantes': estudiantes.count(),
                'total_externos': externos.count(),
            })

        context = {
            'asistentes_data': asistentes_data,
            'title': 'Reporte de Registros por Asistente',
        }

        return render(request, 'admin/asistente_reporte.html', context)

    ver_reporte_registros.short_description = "📊 Ver reporte detallado de registros"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'category', 'severity', 'action', 'username', 'ip_address', 'success', 'message']
    list_filter = ['category', 'severity', 'action', 'success', 'timestamp']
    search_fields = ['username', 'ip_address', 'message', 'path']
    readonly_fields = ['timestamp', 'category', 'severity', 'action', 'user', 'username',
                      'ip_address', 'user_agent', 'path', 'method', 'message',
                      'details', 'success', 'status_code']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        # No permitir crear logs manualmente desde el admin
        return False

    def has_change_permission(self, request, obj=None):
        # No permitir editar logs (son inmutables)
        return False

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar logs
        return request.user.is_superuser