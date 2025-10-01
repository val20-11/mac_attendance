from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from .models import Event, ExternalUser
from .serializers import EventSerializer, ExternalUserSerializer
import random
import string

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
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def register_external_user(request):
    """Registrar un usuario externo: 3 registros por hora por IP"""
    data = request.data
    
    # Generar ID temporal único
    temp_id = 'EXT' + ''.join(random.choices(string.digits, k=7))
    
    # Verificar que no exista
    while ExternalUser.objects.filter(temporary_id=temp_id).exists():
        temp_id = 'EXT' + ''.join(random.choices(string.digits, k=7))
    
    try:
        external_user = ExternalUser.objects.create(
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone', ''),
            institution=data.get('institution'),
            position=data.get('position', ''),
            reason=data.get('reason'),
            temporary_id=temp_id,
            status='pending'
        )
        
        return Response({
            'message': 'Solicitud enviada exitosamente. Tu ID temporal es: ' + temp_id,
            'temporary_id': temp_id,
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error al registrar: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

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