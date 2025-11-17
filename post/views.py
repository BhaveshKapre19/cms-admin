from .models import Post
from .serializers import PostSerializer
from rest_framework import viewsets , status , generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAdminUser,IsAuthenticated


class PostViewset(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_superuser:
            return Post.all_objects.all()
        
        if user.is_authenticated:
            return Post.all_objects.filter(author=user)
        
        return Post.objects.filter(is_published=True)


    def get_permissions(self):
        print(f"Current action is = {self.action}")
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

    
    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user == post.author:
            post.delete()
            return Response(status=status.HTTP_202_ACCEPTED,data={"message":f"the post {post.title} is deleted sucessfully"})
        return Response(status=status.HTTP_401_UNAUTHORIZED,data={"message":"you cannot delete someone else post"})
    
    