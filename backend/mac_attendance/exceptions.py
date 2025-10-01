"""
Manejadores de excepciones personalizados para el proyecto
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.exceptions import Ratelimited


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado que incluye soporte para
    excepciones de rate limiting
    """
    # Manejar excepciones de rate limiting
    if isinstance(exc, Ratelimited):
        data = {
            'error': 'Demasiadas solicitudes. Por favor, intenta más tarde.',
            'detail': 'Has excedido el límite de solicitudes permitidas. Espera unos momentos antes de intentar nuevamente.'
        }
        return Response(data, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Llamar al manejador de excepciones por defecto de DRF para otras excepciones
    response = exception_handler(exc, context)

    return response