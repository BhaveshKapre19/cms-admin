from django.urls import path, include
from rest_framework import routers
from .views import PostViewset

router = routers.DefaultRouter()
router.register(r'', PostViewset, basename='post')

urlpatterns = [
    path('', include(router.urls)),
]
