from django.urls import path , include

urlpatterns = [
    path('',include('post.urls')),
    path('users/',include('user_management.urls')),
    path('files/',include('fileGallery.urls')),
]