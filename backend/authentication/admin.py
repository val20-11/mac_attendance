from django.contrib import admin
from django.contrib.auth.models import User, Group
from django import forms
from django.utils.html import format_html
from django.http import HttpResponse
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import UserProfile, Asistente, ExternalUser, SystemConfiguration, Student, AssistantProfile
from .audit import AuditLog

# Ocultar modelos de Django que no se usan
admin.site.unregister(User)
admin.site.unregister(Group)


# ===== RECURSOS PARA IMPORT/EXPORT =====

class StudentResource(resources.ModelResource):
    """Recurso para importar/exportar SOLO estudiantes"""

    class Meta:
        model = UserProfile
        fields = ('account_number', 'full_name')
        export_order = ('account_number', 'full_name')
        import_id_fields = ['account_number']
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Validar y limpiar datos antes de importar"""
        # Limpiar espacios
        row['account_number'] = str(row.get('account_number', '')).strip()
        row['full_name'] = str(row.get('full_name', '')).strip()
        # Asignar automáticamente user_type como student
        row['user_type'] = 'student'

    def after_save_instance(self, instance, using_transactions, dry_run):
        """Crear usuario de Django si no existe y asegurar que sea estudiante"""
        if not dry_run:
            # Asegurar que sea estudiante
            if instance.user_type != 'student':
                instance.user_type = 'student'
                instance.save()

            # Crear usuario de Django si no existe
            if not instance.user_id:
                user = User.objects.create_user(
                    username=instance.account_number,
                    first_name=instance.full_name,
                    password=None
                )
                user.set_unusable_password()
                user.save()
                instance.user = user
                instance.save()


class AssistantResource(resources.ModelResource):
    """Recurso para importar/exportar SOLO asistentes"""

    class Meta:
        model = UserProfile
        fields = ('account_number', 'full_name')
        export_order = ('account_number', 'full_name')
        import_id_fields = ['account_number']
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Validar y limpiar datos antes de importar"""
        # Limpiar espacios
        row['account_number'] = str(row.get('account_number', '')).strip()
        row['full_name'] = str(row.get('full_name', '')).strip()
        # Asignar automáticamente user_type como assistant
        row['user_type'] = 'assistant'

    def after_save_instance(self, instance, using_transactions, dry_run):
        """Crear usuario de Django si no existe y asegurar que sea asistente"""
        if not dry_run:
            # Asegurar que sea asistente
            if instance.user_type != 'assistant':
                instance.user_type = 'assistant'
                instance.save()

            # Crear usuario de Django si no existe
            if not instance.user_id:
                user = User.objects.create_user(
                    username=instance.account_number,
                    first_name=instance.full_name,
                    password=None
                )
                user.set_unusable_password()
                user.save()
                instance.user = user
                instance.save()


class UserProfileResource(resources.ModelResource):
    """Recurso para importar/exportar UserProfile (LEGACY - no usar)"""

    class Meta:
        model = UserProfile
        fields = ('account_number', 'full_name', 'user_type')
        import_id_fields = ['account_number']
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Validar y limpiar datos antes de importar"""
        # Limpiar espacios
        row['account_number'] = str(row.get('account_number', '')).strip()
        row['full_name'] = str(row.get('full_name', '')).strip()
        row['user_type'] = str(row.get('user_type', '')).strip().lower()

    def after_save_instance(self, instance, using_transactions, dry_run):
        """Crear usuario de Django si no existe"""
        if not dry_run and not instance.user_id:
            user = User.objects.create_user(
                username=instance.account_number,
                first_name=instance.full_name,
                password=None
            )
            user.set_unusable_password()
            user.save()
            instance.user = user
            instance.save()


class ExternalUserResource(resources.ModelResource):
    """Recurso para exportar usuarios externos"""
    approved_by_name = fields.Field()

    class Meta:
        model = ExternalUser
        fields = ('account_number', 'full_name', 'status', 'approved_by_name', 'created_at', 'rejection_reason')
        export_order = fields

    def dehydrate_approved_by_name(self, external_user):
        """Obtener nombre del aprobador"""
        return external_user.approved_by.full_name if external_user.approved_by else '-'


class UserProfileForm(forms.ModelForm):
    """Formulario personalizado para crear UserProfile sin contraseña"""

    class Meta:
        model = UserProfile
        fields = ['account_number', 'full_name', 'user_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo user_type obligatorio
        self.fields['user_type'].required = True
        self.fields['user_type'].empty_label = None  # Quitar opción vacía del dropdown

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


class StudentAdmin(ImportExportModelAdmin):
    """Admin SOLO para estudiantes"""
    resource_class = StudentResource
    list_display = ['account_number', 'full_name']
    search_fields = ['account_number', 'full_name']
    actions = ['export_selected_students']

    fieldsets = (
        ('Información del Estudiante', {
            'fields': ('account_number', 'full_name'),
            'description': '📚 Importa el Excel con solo 2 columnas: account_number y full_name. El sistema automáticamente los creará como estudiantes.'
        }),
    )

    def get_queryset(self, request):
        """Mostrar SOLO estudiantes"""
        qs = super().get_queryset(request)
        return qs.filter(user_type='student')

    def get_import_formats(self):
        """Formatos permitidos para importar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def get_export_formats(self):
        """Formatos permitidos para exportar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def export_selected_students(self, request, queryset):
        """Acción para exportar estudiantes seleccionados"""
        resource = StudentResource()
        dataset = resource.export(queryset)

        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="estudiantes.xlsx"'

        self.message_user(request, f'Se exportaron {queryset.count()} estudiantes.')
        return response

    export_selected_students.short_description = "📊 Exportar estudiantes seleccionados"

    def save_model(self, request, obj, form, change):
        """Asegurar que siempre sea estudiante"""
        obj.user_type = 'student'
        super().save_model(request, obj, form, change)


class AssistantProfileAdmin(ImportExportModelAdmin):
    """Admin SOLO para asistentes"""
    resource_class = AssistantResource
    list_display = ['account_number', 'full_name']
    search_fields = ['account_number', 'full_name']
    actions = ['export_selected_assistants']

    fieldsets = (
        ('Información del Asistente', {
            'fields': ('account_number', 'full_name'),
            'description': '👨‍🏫 Importa el Excel con solo 2 columnas: account_number y full_name. El sistema automáticamente los creará como asistentes.'
        }),
    )

    def get_queryset(self, request):
        """Mostrar SOLO asistentes"""
        qs = super().get_queryset(request)
        return qs.filter(user_type='assistant')

    def get_import_formats(self):
        """Formatos permitidos para importar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def get_export_formats(self):
        """Formatos permitidos para exportar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def export_selected_assistants(self, request, queryset):
        """Acción para exportar asistentes seleccionados"""
        resource = AssistantResource()
        dataset = resource.export(queryset)

        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="asistentes.xlsx"'

        self.message_user(request, f'Se exportaron {queryset.count()} asistentes.')
        return response

    export_selected_assistants.short_description = "📊 Exportar asistentes seleccionados"

    def save_model(self, request, obj, form, change):
        """Asegurar que siempre sea asistente"""
        obj.user_type = 'assistant'
        super().save_model(request, obj, form, change)


# Registrar los admins separados con proxy models
admin.site.register(Student, StudentAdmin)
admin.site.register(AssistantProfile, AssistantProfileAdmin)


# UserProfile está oculto del admin - se usan Student y AssistantProfile en su lugar


@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'get_registros_realizados', 'ver_alumnos_registrados', 'can_manage_events']
    list_filter = ['can_manage_events']
    search_fields = ['user_profile__full_name', 'user_profile__account_number']
    readonly_fields = ['get_registros_realizados', 'get_ultimos_registros']
    actions = ['ver_reporte_registros']

    fieldsets = (
        ('Información del Asistente', {
            'fields': ('user_profile',)
        }),
        ('Permisos y Configuración', {
            'fields': ('can_manage_events',)
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


@admin.register(ExternalUser)
class ExternalUserAdmin(ImportExportModelAdmin):
    resource_class = ExternalUserResource
    list_display = ['account_number', 'full_name', 'get_status', 'get_approved_by', 'created_at']
    list_filter = ['status', 'created_at', 'approved_by']
    search_fields = ['full_name', 'account_number', 'approved_by__full_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'processed_at']
    date_hierarchy = 'created_at'
    actions = ['export_selected_external_users']

    fieldsets = (
        ('Información Personal', {
            'fields': ('account_number', 'full_name')
        }),
        ('Estado de Aprobación', {
            'fields': ('status', 'approved_by', 'processed_at', 'rejection_reason', 'created_at')
        }),
    )

    def get_export_formats(self):
        """Solo exportar (no importar usuarios externos)"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def has_import_permission(self, request):
        """No permitir importar usuarios externos (se crean desde la app)"""
        return False

    def export_selected_external_users(self, request, queryset):
        """Acción para exportar usuarios externos seleccionados"""
        resource = ExternalUserResource()
        dataset = resource.export(queryset)

        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="usuarios_externos.xlsx"'

        self.message_user(request, f'Se exportaron {queryset.count()} usuarios externos.')
        return response

    export_selected_external_users.short_description = "📊 Exportar usuarios externos seleccionados"

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


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['get_config_name', 'minimum_attendance_percentage', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at', 'updated_by']

    fieldsets = (
        ('Configuración de Asistencia', {
            'fields': ('minimum_attendance_percentage',),
            'description': '⚙️ Este porcentaje se aplica a TODOS los estudiantes del sistema. Define el porcentaje mínimo de asistencia requerido para obtener la constancia.'
        }),
        ('Información de Auditoría', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def get_config_name(self, obj):
        return "Configuración Global del Sistema"
    get_config_name.short_description = 'Configuración'

    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not SystemConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False

    def save_model(self, request, obj, form, change):
        # Registrar quién actualizó la configuración
        try:
            obj.updated_by = request.user.profile
        except:
            pass
        super().save_model(request, obj, form, change)