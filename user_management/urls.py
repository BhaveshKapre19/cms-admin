from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, VerifyOtpView, LoginView, UserViewSet , ForgetPasswordView,ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register('profile', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('forget-password/',ForgetPasswordView.as_view(),name="forget-password"),
    path('reset-password/',ResetPasswordView.as_view(),name="reset-password"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
