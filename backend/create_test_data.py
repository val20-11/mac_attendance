#!/usr/bin/env python
"""Script para crear datos de prueba para el sistema de asistencia"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile, Asistente
from events.models import Event
from attendance.models import Attendance, AttendanceStats
from datetime import date, time

def create_test_data():
    print("[+] Creando datos de prueba...")

    # Obtener o crear un asistente para registrar asistencias
    try:
        asistente_profile = UserProfile.objects.get(user_type='assistant')
        print(f"[OK] Asistente encontrado: {asistente_profile.full_name}")
    except UserProfile.DoesNotExist:
        print("[ERROR] No hay asistentes en el sistema. Por favor crea uno primero.")
        return

    # Crear 5 estudiantes de prueba
    estudiantes_data = [
        ('3001001', 'María González López', 90.0),  # Cumple
        ('3001002', 'Juan Pérez Martínez', 85.0),   # Cumple
        ('3001003', 'Ana Rodríguez Sánchez', 75.0), # NO cumple
        ('3001004', 'Carlos López García', 95.0),   # Cumple
        ('3001005', 'Laura Martínez Ruiz', 60.0),   # NO cumple
    ]

    estudiantes = []
    for account, name, percentage in estudiantes_data:
        # Verificar si ya existe
        if UserProfile.objects.filter(account_number=account).exists():
            print(f"[SKIP] Estudiante {account} ya existe, omitiendo...")
            estudiantes.append(UserProfile.objects.get(account_number=account))
            continue

        # Crear usuario Django
        user = User.objects.create_user(
            username=account,
            first_name=name,
            password=None
        )
        user.set_unusable_password()
        user.save()

        # Crear perfil
        profile = UserProfile.objects.create(
            user=user,
            account_number=account,
            full_name=name,
            user_type='student'
        )
        estudiantes.append(profile)
        print(f"[OK] Estudiante creado: {name} ({account})")

    # Crear 3 eventos de prueba (en diferentes horarios para evitar conflictos)
    eventos_data = [
        ('Conferencia de Inteligencia Artificial', 'Dr. Roberto Silva', time(9, 0), time(11, 0)),
        ('Taller de Python Avanzado', 'Ing. Patricia Gómez', time(12, 0), time(14, 0)),
        ('Seminario de Ciberseguridad', 'M.C. Fernando Ruiz', time(15, 0), time(17, 0)),
    ]

    eventos = []
    for title, speaker, start, end in eventos_data:
        # Verificar si ya existe
        if Event.objects.filter(title=title).exists():
            print(f"[SKIP] Evento '{title}' ya existe, omitiendo...")
            eventos.append(Event.objects.get(title=title))
            continue

        evento = Event.objects.create(
            title=title,
            speaker=speaker,
            date=date(2025, 10, 15),
            start_time=start,
            end_time=end,
            event_type='lecture',
            modality='presential',
            location='Auditorio Principal',
            description=f'Descripción de {title}',
            created_by=asistente_profile,
            is_active=True
        )
        eventos.append(evento)
        print(f"[OK] Evento creado: {title}")

    # Crear asistencias simuladas para generar los porcentajes
    print("\n[+] Creando estadisticas de asistencia simuladas...")

    for i, (profile, (_, _, target_percentage)) in enumerate(zip(estudiantes, estudiantes_data)):
        # Crear o actualizar estadísticas
        stats, created = AttendanceStats.objects.get_or_create(
            student=profile,
            defaults={
                'total_events': len(eventos),
                'attended_events': 0,
                'attendance_percentage': 0.0
            }
        )

        # Calcular eventos a asistir para lograr el porcentaje deseado
        total_eventos = len(eventos)
        eventos_a_asistir = int((target_percentage / 100) * total_eventos)

        # Registrar asistencias
        for j in range(eventos_a_asistir):
            if j < len(eventos):
                # Verificar si ya existe la asistencia
                if not Attendance.objects.filter(student=profile, event=eventos[j]).exists():
                    Attendance.objects.create(
                        student=profile,
                        event=eventos[j],
                        registered_by=asistente_profile,
                        registration_method='manual',
                        is_valid=True
                    )

        # Actualizar estadísticas
        stats.update_stats()
        print(f"   {profile.full_name}: {stats.attendance_percentage}% de asistencia")

    print("\n[OK] Datos de prueba creados exitosamente!")
    print(f"\n[RESUMEN]")
    print(f"   - Estudiantes: {len(estudiantes)}")
    print(f"   - Eventos: {len(eventos)}")
    print(f"   - Porcentaje minimo: 80%")
    print(f"\n[INFO] Ahora puedes probar:")
    print(f"   1. Ir a http://127.0.0.1:8000/admin/")
    print(f"   2. Navegar a 'Estadisticas de asistencia'")
    print(f"   3. Seleccionar todos los registros")
    print(f"   4. Usar la accion: 'Exportar estudiantes que cumplen requisito para constancia'")

if __name__ == '__main__':
    create_test_data()
