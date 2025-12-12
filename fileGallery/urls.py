from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FileGalleryViewSet

router = DefaultRouter()
router.register(r'file-gallery', FileGalleryViewSet, basename='filegallery')

urlpatterns = router.urls + [
    
]
