from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from authentication.models import UserProfile
from events.models import Event
from .models import Attendance, AttendanceStats

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='60/m', method='POST', block=True)
def register_attendance(request):
    """Registrar asistencia - Solo asistentes: 60 registros por minuto"""
    if request.method == 'GET':
        return Response({
            'message': 'API de registro de asistencia activa',
            'methods': ['POST'],
            'required_fields': ['event_id', 'account_number']
        })

    # Verificar que el usuario autenticado sea asistente
    try:
        registrar_profile = request.user.userprofile
        if registrar_profile.user_type != 'assistant':
            return Response({
                'error': 'Solo los asistentes pueden registrar asistencias'
            }, status=status.HTTP_403_FORBIDDEN)
    except:
        return Response({
            'error': 'Usuario sin perfil válido'
        }, status=status.HTTP_403_FORBIDDEN)

    event_id = request.data.get('event_id')
    account_number = request.data.get('account_number')
    
    if not event_id or not account_number:
        return Response({
            'error': 'Se requiere event_id y account_number'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Buscar evento
    try:
        event = Event.objects.get(id=event_id, is_active=True)
    except Event.DoesNotExist:
        return Response({
            'error': 'Evento no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Buscar estudiante
    try:
        student_profile = UserProfile.objects.get(
            account_number=account_number,
            user_type='student'
        )
    except UserProfile.DoesNotExist:
        return Response({
            'error': f'Estudiante con número de cuenta {account_number} no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Usar el asistente autenticado como registrador
    assistant_profile = registrar_profile
    
    # Verificar si ya tiene asistencia
    if Attendance.objects.filter(student=student_profile, event=event, is_valid=True).exists():
        return Response({
            'error': 'El estudiante ya tiene asistencia registrada para este evento'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Crear asistencia
    try:
        attendance = Attendance.objects.create(
            student=student_profile,
            event=event,
            registered_by=assistant_profile,
            registration_method='manual'
        )
        
        return Response({
            'message': f'Asistencia registrada para {student_profile.full_name}',
            'attendance_id': attendance.id,
            'event': event.title,
            'registered_by': assistant_profile.full_name
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error al crear asistencia: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='30/m', method='GET', block=True)
def get_student_stats(request):
    """Obtener estadísticas de estudiante: 30 consultas por minuto"""
    account_number = request.GET.get('account_number')

    if not account_number:
        return Response({'error': 'Se requiere account_number'}, status=400)

    # Verificar permisos: estudiantes solo pueden ver sus propias estadísticas
    try:
        requester_profile = request.user.userprofile

        # Si es estudiante, solo puede consultar sus propias estadísticas
        if requester_profile.user_type == 'student':
            if requester_profile.account_number != account_number:
                return Response({
                    'error': 'Solo puedes consultar tus propias estadísticas'
                }, status=status.HTTP_403_FORBIDDEN)
        # Asistentes pueden ver estadísticas de cualquier estudiante
        elif requester_profile.user_type != 'assistant':
            return Response({
                'error': 'No tienes permisos para consultar estadísticas'
            }, status=status.HTTP_403_FORBIDDEN)
    except:
        return Response({
            'error': 'Usuario sin perfil válido'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        student_profile = UserProfile.objects.get(
            account_number=account_number,
            user_type='student'
        )
        stats, created = AttendanceStats.objects.get_or_create(
            student=student_profile
        )
        stats.update_stats()

        return Response({
            'total_events': stats.total_events,
            'attended_events': stats.attended_events,
            'attendance_percentage': stats.attendance_percentage
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='60/m', method='GET', block=True)
def get_recent_attendances(request):
    """Obtener asistencias recientes - Solo asistentes: 60 consultas por minuto"""
    # Solo asistentes pueden ver asistencias recientes
    try:
        requester_profile = request.user.userprofile
        if requester_profile.user_type != 'assistant':
            return Response({
                'error': 'Solo los asistentes pueden consultar asistencias recientes'
            }, status=status.HTTP_403_FORBIDDEN)
    except:
        return Response({
            'error': 'Usuario sin perfil válido'
        }, status=status.HTTP_403_FORBIDDEN)

    recent = Attendance.objects.select_related('student', 'event').order_by('-timestamp')[:5]

    data = []
    for attendance in recent:
        data.append({
            'attendee_name': attendance.attendee_name,
            'event_title': attendance.event.title,
            'timestamp': attendance.timestamp.strftime('%H:%M')
        })

    return Response(data)