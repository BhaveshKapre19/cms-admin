from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser , IsAuthenticatedOrReadOnly
from django.db import models

from .models import Post, Category
from .serializers import PostSerializer, CategorySerializer
from rest_framework.decorators import action
from user_management.permissions import IsUserActive,IsVerifiedUser

class PostViewset(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user

        # Admin can see everything
        if user.is_authenticated and user.is_superuser:
            return Post.all_objects.all()

        # Logged-in user → only their posts
        if user.is_authenticated:
            return Post.all_objects.filter(author=user)

        # Public → only published posts
        return Post.objects.filter(is_published=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]

        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'draft', 'publish']:
            permission_classes = [IsAuthenticated, IsUserActive, IsVerifiedUser]

        else:
            permission_classes = [IsAdminUser]

        return [perm() for perm in permission_classes]

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()

        if not (request.user.is_superuser or request.user == post.author):
            return Response(
                {"message": "You cannot delete someone else's post"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post.delete()
        return Response(
            {"message": f"Post '{post.title}' deleted successfully"},
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=True, methods=['post'])
    def draft(self, request, *args, **kwargs):
        post = self.get_object()

        if request.user != post.author and not request.user.is_superuser:
            return Response(
                {"message": "You cannot draft someone else's post"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post.is_published = False
        post.save()
        return Response(
            {"message": f"Post '{post.title}' drafted successfully"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, *args, **kwargs):
        post = self.get_object()

        if request.user != post.author and not request.user.is_superuser:
            return Response(
                {"message": "You cannot publish someone else's post"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        post.is_published = True
        post.save()
        return Response(
            {"message": f"Post '{post.title}' published successfully"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'])
    def restore(self, request, *args, **kwargs):
        post = self.get_object()

        if not post.is_deleted:
            return Response(
                {"message": f"Post '{post.title}' is not archived"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not (request.user.is_superuser or request.user == post.author):
            return Response(
                {"message": "You cannot restore this post"},
                status=status.HTTP_403_FORBIDDEN
            )

        post.restore()
        return Response(
            {"message": f"Post '{post.title}' restored successfully"},
            status=status.HTTP_200_OK
        )


class CategoryViewset(viewsets.ModelViewSet):
    """
    Get categories list + detail by slug.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated,IsVerifiedUser, IsUserActive]
        else:
            permission_classes = [IsAdminUser]
        return [perm() for perm in permission_classes]
    
