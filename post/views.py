from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser , IsAuthenticatedOrReadOnly
from django.db import models

from .models import Post, Category
from .serializers import PostSerializer, CategorySerializer


class PostViewset(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_superuser:
            return Post.all_objects.all()

        if user.is_authenticated:
            return Post.all_objects.filter(
                models.Q(is_published=True) |
                models.Q(author=user)
            )

        return Post.objects.filter(is_published=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]

        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]

        else:
            permission_classes = [IsAdminUser]

        return [perm() for perm in permission_classes]

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()

        if request.user != post.author:
            return Response(
                {"message": "You cannot delete someone else's post"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post.delete()
        return Response(
            {"message": f"Post '{post.title}' deleted successfully"},
            status=status.HTTP_202_ACCEPTED
        )



class CategoryViewset(viewsets.ModelViewSet):
    """
    Get categories list + detail by slug.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
