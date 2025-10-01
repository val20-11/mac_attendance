from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from .models import UserProfile, Asistente
from .serializers import LoginSerializer, UserSerializer
from .audit import AuditLog

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    """Login con rate limiting: 5 intentos por minuto por IP"""
    serializer = LoginSerializer(data=request.data)
    account_number = request.data.get('account_number', 'unknown')

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)

        # Log exitoso
        AuditLog.log(
            category='AUTH',
            action='LOGIN_SUCCESS',
            message=f'Login exitoso para cuenta {account_number}',
            request=request,
            user=user,
            severity='INFO',
            success=True,
            status_code=200,
            account_number=account_number
        )

        return Response({
            'message': 'Login exitoso',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })

    # Log fallido
    AuditLog.log(
        category='AUTH',
        action='LOGIN_FAILED',
        message=f'Intento de login fallido para cuenta {account_number}',
        request=request,
        severity='WARNING',
        success=False,
        status_code=400,
        account_number=account_number,
        errors=str(serializer.errors)
    )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Log logout
    AuditLog.log(
        category='AUTH',
        action='LOGOUT',
        message=f'Logout de usuario {request.user.username}',
        request=request,
        user=request.user,
        severity='INFO',
        success=True,
        status_code=200
    )

    logout(request)
    return Response({'message': 'Logout exitoso'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    return Response(UserSerializer(request.user).data)

@api_view(['GET'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='30/m', method='GET', block=True)
def check_auth_status(request):
    """Verificar estado de autenticación: 30 consultas por minuto por IP"""
    if request.user.is_authenticated:
        return Response({
            'is_authenticated': True,
            'user': UserSerializer(request.user).data
        })
    return Response({'is_authenticated': False})

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def refresh_token(request):
    """Refrescar access token: 10 intentos por minuto por IP"""
    from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
    from rest_framework_simplejwt.serializers import TokenRefreshSerializer

    serializer = TokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({'error': 'Token inválido o expirado'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """Verificar si el token actual es válido"""
    return Response({
        'valid': True,
        'user': UserSerializer(request.user).data
    })