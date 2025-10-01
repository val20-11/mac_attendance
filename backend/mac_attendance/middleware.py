"""
Middleware de auditoría para capturar eventos de seguridad
"""
from authentication.audit import AuditLog
from django_ratelimit.exceptions import Ratelimited


class AuditMiddleware:
    """
    Middleware para registrar eventos de seguridad automáticamente
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la solicitud
        response = self.get_response(request)

        # Registrar eventos de seguridad basados en código de respuesta
        self._log_security_events(request, response)

        return response

    def _log_security_events(self, request, response):
        """
        Registrar eventos de seguridad basados en códigos de respuesta HTTP
        """
        status_code = response.status_code
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

        # 401 Unauthorized - Acceso no autorizado
        if status_code == 401:
            AuditLog.log(
                category='SECURITY',
                action='ACCESS_DENIED',
                message=f'Intento de acceso no autorizado a {request.path}',
                request=request,
                user=user,
                severity='WARNING',
                success=False,
                status_code=401,
                path=request.path,
                method=request.method
            )

        # 403 Forbidden - Permisos insuficientes
        elif status_code == 403:
            AuditLog.log(
                category='SECURITY',
                action='ACCESS_DENIED',
                message=f'Acceso denegado (permisos insuficientes) a {request.path}',
                request=request,
                user=user,
                severity='WARNING',
                success=False,
                status_code=403,
                path=request.path,
                method=request.method
            )

        # 429 Too Many Requests - Rate limit exceeded
        elif status_code == 429:
            AuditLog.log(
                category='SECURITY',
                action='RATE_LIMITED',
                message=f'Rate limit excedido para {request.path}',
                request=request,
                user=user,
                severity='WARNING',
                success=False,
                status_code=429,
                path=request.path,
                method=request.method
            )

    def process_exception(self, request, exception):
        """
        Capturar excepciones de rate limiting
        """
        if isinstance(exception, Ratelimited):
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

            AuditLog.log(
                category='SECURITY',
                action='RATE_LIMITED',
                message=f'Rate limit exception en {request.path}',
                request=request,
                user=user,
                severity='WARNING',
                success=False,
                status_code=429,
                path=request.path,
                method=request.method,
                exception=str(exception)
            )

        return None  # Permitir que Django maneje la excepción normalmente