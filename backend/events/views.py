from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from django.db import models
from .models import Event
from authentication.models import ExternalUser
from .serializers import EventSerializer, ExternalUserSerializer
import re

class EventListView(generics.ListCreateAPIView):
    queryset = Event.objects.filter(is_active=True)
    serializer_class = EventSerializer

    def get_permissions(self):
        """Permitir lectura pública, pero creación solo para autenticados"""
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        return Event.objects.filter(is_active=True).order_by('date', 'start_time')

    def perform_create(self, serializer):
        """Verificar que solo asistentes puedan crear eventos"""
        try:
            user_profile = self.request.user.userprofile
            if user_profile.user_type != 'assistant':
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Solo los asistentes pueden crear eventos')
        except:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Usuario sin perfil válido')

        serializer.save()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='30/m', method='POST', block=True)
def register_external_user(request):
    """Crear un usuario externo - Solo asistentes: 30 creaciones por minuto"""
    # Verificar que el usuario sea asistente
    try:
        user_profile = request.user.userprofile
        if user_profile.user_type != 'assistant':
            return Response({'error': 'Solo los asistentes pueden crear usuarios externos'}, status=403)
    except:
        return Response({'error': 'Usuario sin perfil válido'}, status=403)

    data = request.data
    account_number = data.get('account_number')
    full_name = data.get('full_name')

    if not account_number or not full_name:
        return Response({'error': 'Número de cuenta y nombre completo son requeridos'}, status=400)

    # Validar formato de número de cuenta (7 dígitos)
    if not re.match(r'^\d{7}$', account_number):
        return Response({'error': 'El número de cuenta debe tener exactamente 7 dígitos'}, status=400)

    # Verificar que no exista en usuarios regulares
    from authentication.models import UserProfile
    if UserProfile.objects.filter(account_number=account_number).exists():
        return Response({'error': 'Este número de cuenta ya está registrado como usuario regular'}, status=400)

    # Verificar que no exista en usuarios externos
    if ExternalUser.objects.filter(account_number=account_number).exists():
        return Response({'error': 'Este número de cuenta ya está registrado como usuario externo'}, status=400)

    try:
        external_user = ExternalUser.objects.create(
            full_name=full_name,
            account_number=account_number,
            status='approved',
            approved_by=user_profile
        )

        return Response({
            'message': 'Usuario externo creado exitosamente',
            'account_number': account_number,
            'full_name': full_name,
            'status': 'approved'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Error al crear usuario externo: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='60/m', method='GET', block=True)
def search_external_users(request):
    """Buscar usuarios externos por nombre o número de cuenta - Solo asistentes: 60 búsquedas por minuto"""
    # Verificar que el usuario sea asistente
    try:
        user_profile = request.user.userprofile
        if user_profile.user_type != 'assistant':
            return Response({'error': 'Solo los asistentes pueden buscar usuarios externos'}, status=403)
    except:
        return Response({'error': 'Usuario sin perfil válido'}, status=403)

    search_query = request.GET.get('q', '').strip()

    if not search_query:
        return Response({'error': 'Parámetro de búsqueda "q" requerido'}, status=400)

    # Buscar por número de cuenta o nombre (contiene)
    external_users = ExternalUser.objects.filter(
        status='approved'
    ).filter(
        models.Q(account_number__icontains=search_query) |
        models.Q(full_name__icontains=search_query)
    )[:10]  # Limitar a 10 resultados

    results = []
    for user in external_users:
        results.append({
            'id': user.id,
            'account_number': user.account_number,
            'full_name': user.full_name,
            'created_at': user.created_at.strftime('%Y-%m-%d')
        })

    return Response({
        'count': len(results),
        'results': results
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='30/m', method='POST', block=True)
def approve_external_user(request, user_id):
    """Aprobar/rechazar usuario externo - Solo asistentes: 30 acciones por minuto"""
    # Verificar que el usuario sea asistente
    try:
        user_profile = request.user.userprofile
        if user_profile.user_type != 'assistant':
            return Response({'error': 'Solo los asistentes pueden aprobar usuarios externos'}, status=403)
    except:
        return Response({'error': 'Usuario sin perfil válido'}, status=403)

    try:
        external_user = ExternalUser.objects.get(id=user_id)
        action = request.data.get('action')  # 'approve' o 'reject'
        
        if action == 'approve':
            external_user.status = 'approved'
            external_user.approved_by = user_profile
            external_user.processed_at = timezone.now()
            external_user.save()
            return Response({'message': 'Usuario aprobado'})
        elif action == 'reject':
            reason = request.data.get('reason', '')
            external_user.status = 'rejected'
            external_user.approved_by = user_profile
            external_user.rejection_reason = reason
            external_user.processed_at = timezone.now()
            external_user.save()
            return Response({'message': 'Usuario rechazado'})
        else:
            return Response({'error': 'Acción inválida'}, status=400)
            
    except ExternalUser.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)