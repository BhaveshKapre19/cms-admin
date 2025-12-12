from django.urls import path, include
from rest_framework import routers
from .views import PostViewset , CategoryViewset

router = routers.DefaultRouter()
router.register(r'posts', PostViewset, basename='post')
router.register(r'categories', CategoryViewset, basename='category')


urlpatterns = [
    path('', include(router.urls)),
]
