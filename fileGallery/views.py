from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly ,AllowAny , IsAuthenticated
from rest_framework.views import APIView
from .models import FileGallery
from .serializers import FileGallerySerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response


class FileGalleryViewSet(ModelViewSet):
    queryset = FileGallery.objects.all().order_by('-uploaded_at')
    serializer_class = FileGallerySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context



