from django.http import JsonResponse
from django.urls import resolve
from django.conf import settings

class MaintenanceModeMiddleware:
    """
    Middleware to handle maintenance mode for admin and blog sections.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Always allow Django admin
        if request.path.startswith("/admin/"):
            return self.get_response(request)
        
        if not settings.MAINTAINANCE:
            return self.get_response(request)

        return JsonResponse(
            {'detail': 'The site is under maintenance. Please try again later.', "key": "MAINTENANCE_MODE","CODE":"MAT503"},
            status=503
        )


class RegistrationCheckMiddleware:
    """
    Middleware to restrict access to registration endpoint when registration is disabled.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/register/" and not settings.ALLOW_REGISTRATION:
            return JsonResponse(
                {'detail': 'User registration is currently disabled.', "key": "REGISTRATION_DISABLED","CODE":"REG403"},
                status=403
            )
        return self.get_response(request)