#!/usr/bin/env python
"""Script para crear datos de prueba VÁLIDOS respetando todas las validaciones"""
import os
import django
from datetime import datetime, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from authentication.models import UserProfile, Asistente
from events.models import Event
from attendance.models import Attendance, AttendanceStats

def create_valid_test_data():
    print("[+] Creando datos de prueba VALIDOS...")

    # Obtener o crear un asistente para registrar asistencias
    try:
        asistente_profile = UserProfile.objects.get(user_type='assistant')
        print(f"[OK] Asistente encontrado: {asistente_profile.full_name}")
    except UserProfile.DoesNotExist:
        print("[ERROR] No hay asistentes en el sistema. Por favor crea uno primero.")
        return

    # Verificar estudiantes existentes
    estudiantes = UserProfile.objects.filter(user_type='student')
    if estudiantes.count() < 3:
        print("[+] Creando estudiantes de prueba...")
        estudiantes_data = [
            ('3001001', 'María González López'),
            ('3001002', 'Juan Pérez Martínez'),
            ('3001003', 'Ana Rodríguez Sánchez'),
            ('3001004', 'Carlos López García'),
            ('3001005', 'Laura Martínez Ruiz'),
        ]

        for account, name in estudiantes_data:
            if UserProfile.objects.filter(account_number=account).exists():
                print(f"[SKIP] Estudiante {account} ya existe")
                continue

            user = User.objects.create_user(
                username=account,
                first_name=name,
                password=None
            )
            user.set_unusable_password()
            user.save()

            UserProfile.objects.create(
                user=user,
                account_number=account,
                full_name=name,
                user_type='student'
            )
            print(f"[OK] Estudiante creado: {name} ({account})")

    estudiantes = list(UserProfile.objects.filter(user_type='student')[:5])
    print(f"[OK] {len(estudiantes)} estudiantes disponibles")

    # Obtener hora actual en timezone local
    now = timezone.now()
    now_local = timezone.localtime(now)
    today = now_local.date()

    print(f"\n[INFO] Fecha/Hora actual (local): {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] Timezone: {timezone.get_current_timezone()}")

    # Crear eventos para HOY con horarios fijos que funcionen
    # Como estamos en la noche, usamos eventos con margen suficiente

    from datetime import date
    tomorrow = (now_local + timedelta(days=1)).date()

    eventos_data = []

    # Evento 1: Mañana 9:00-11:00 (aún no permite asistencias)
    eventos_data.append((
        'Introducción a la Inteligencia Artificial',
        'Dr. Luis Martínez',
        time(9, 0),
        time(11, 0),
        tomorrow
    ))

    # Evento 2: Mañana 13:00-15:00 (aún no permite asistencias)
    eventos_data.append((
        'Análisis de Datos con Python',
        'Ing. Patricia Gómez',
        time(13, 15),
        time(15, 0),
        tomorrow
    ))

    # Evento 3: Mañana 16:00-18:00 (aún no permite asistencias)
    eventos_data.append((
        'Taller de Machine Learning',
        'Dra. Ana López',
        time(16, 0),
        time(18, 0),
        tomorrow
    ))

    eventos = []
    for title, speaker, start, end, event_date in eventos_data:
        # Verificar si ya existe
        if Event.objects.filter(title=title, date=event_date).exists():
            print(f"[SKIP] Evento '{title}' ya existe")
            eventos.append(Event.objects.get(title=title, date=event_date))
            continue

        evento = Event.objects.create(
            title=title,
            speaker=speaker,
            date=event_date,
            start_time=start,
            end_time=end,
            event_type='lecture',
            modality='presential',
            location='Auditorio Principal',
            description=f'Evento de prueba: {title}',
            created_by=asistente_profile,
            is_active=True
        )
        eventos.append(evento)
        print(f"[OK] Evento creado: {title} ({event_date} {start.strftime('%H:%M')}-{end.strftime('%H:%M')})")

    # Intentar crear asistencias (TODAS deberían fallar porque los eventos son mañana)
    print("\n[+] Intentando registrar asistencias para eventos de mañana...")
    print("[NOTA] TODAS las asistencias deberían fallar porque los eventos son mañana")

    asistencias_creadas = 0
    for i, evento in enumerate(eventos):
        estudiante = estudiantes[i] if i < len(estudiantes) else estudiantes[0]
        print(f"\n[TEST] Intentando registrar en: {evento.title} ({evento.date} {evento.start_time})")
        try:
            # Verificar si ya existe
            if Attendance.objects.filter(student=estudiante, event=evento).exists():
                print(f"   [SKIP] {estudiante.full_name} ya tiene asistencia")
                continue

            att = Attendance.objects.create(
                student=estudiante,
                event=evento,
                registered_by=asistente_profile,
                registration_method='manual',
                is_valid=True
            )
            print(f"   [ERROR] Se permitió registro (NO DEBERÍA) - Asistencia: {estudiante.full_name}")
            asistencias_creadas += 1
        except Exception as e:
            error_msg = str(e)
            if "No se puede registrar asistencia antes del evento" in error_msg:
                print(f"   [OK] Validación funcionó correctamente - Evento es mañana")
            else:
                print(f"   [OK] Validación funcionó: {error_msg[:80]}...")

    # Actualizar estadísticas
    print("\n[+] Actualizando estadísticas...")
    for estudiante in estudiantes:
        stats, created = AttendanceStats.objects.get_or_create(student=estudiante)
        stats.update_stats()
        print(f"   {estudiante.full_name}: {stats.attendance_percentage}% asistencia")

    print("\n" + "="*70)
    print("[OK] Datos de prueba creados exitosamente!")
    print("="*70)
    print(f"\n[RESUMEN]")
    print(f"   - Estudiantes: {len(estudiantes)}")
    print(f"   - Eventos creados: {len(eventos)}")
    print(f"   - Asistencias válidas: {asistencias_creadas}")
    print(f"   - Fecha/Hora: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n[INFO] Ahora puedes:")
    print(f"   1. Ir a http://127.0.0.1:8000/admin/")
    print(f"   2. Ver eventos en 'Events' - eventos para mañana {tomorrow}")
    print(f"   3. Ver asistencias en 'Attendances' - debería estar vacío")
    print(f"   4. Ver estadísticas en 'Attendance stats'")
    print(f"\n[NOTA] Las asistencias solo se pueden registrar durante los eventos")
    print(f"[NOTA] Mañana {tomorrow} a partir de las 8:50 AM se podrán registrar asistencias")

if __name__ == '__main__':
    create_valid_test_data()
