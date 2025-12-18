"""
URL configuration for cms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    if getattr(settings, "MAINTENANCE", False):
        return JsonResponse(
            {'detail': 'The site is under maintenance. Please try again later.', "key": "MAINTENANCE_MODE","CODE":"MAT503"},
            status=503
        )

    return JsonResponse(
        {
            "status": "healthy",
            "maintenance": False
        },
        status=200
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('cms.apis')),
    path('health-check/', health_check),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
