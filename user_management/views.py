from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated , IsAdminUser , IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminOrOwner, IsVerifiedUser, IsUserActive
from rest_framework.decorators import action

from .models import UserModel
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    EmailOtpSerializer,
    ForgotPasswordRequestSerializer,
    ResetPasswordSerializer
)



# ---------------------------------
# Helper Function - JWT Token Generator
# ---------------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ---------------------------------
# Registration API
# ---------------------------------
class RegisterView(generics.CreateAPIView):
    """Registers a new user and sends OTP."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(f"register user method called here {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer)
        user = serializer.save()
        print(user)
        return Response({
            "message": "User registered successfully. Please verify your email using the OTP sent.",
            "user": UserSerializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)


# ---------------------------------
# OTP Verification API
# ---------------------------------
class VerifyOtpView(APIView):
    """Verifies user's email using OTP."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "Email verified successfully!",
        }, status=status.HTTP_200_OK)


# ---------------------------------
# Login API (JWT Token)
# ---------------------------------
class LoginView(APIView):
    """Authenticate user with email & password, returns JWT + user data."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user, context={"request": request}).data
        
        return Response({
            "message": "Login successful",
            "refresh": tokens['refresh'],
            "access": tokens['access'],
            "user": user_data
        }, status=status.HTTP_200_OK)


# ---------------------------------
# User ViewSet (CRUD for profile)
# ---------------------------------
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profile."""
    queryset = UserModel.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated , IsAdminOrOwner]

    def perform_destroy(self, instance):
        """Soft delete user."""
        instance.is_deleted = True
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def lock(self, request,slug=None):
        """Admin can lock a user account."""
        user = self.get_object()
        if user.is_superuser:
            return Response({"message": "Cannot lock a superuser account."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"message": f"User '{user.email}' is already locked."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.is_active = False
            user.save()
            return Response({"message": f"User '{user.email}' has been locked."}, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def unlock(self, request,slug=None):
        """Admin can unlock a user account."""
        user = self.get_object()
        if user.is_active:
            return Response({"message": f"User '{user.email}' is already active."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.is_active = True
            user.save()
            return Response({"message": f"User '{user.email}' has been unlocked."}, status=status.HTTP_200_OK)



class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = ForgotPasswordRequestSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK,data={"message":"check your email for the otp"})
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer.errors)

    

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK,data={"message":"your password is reset successfully"})
        return Response(status=status.HTTP_400_BAD_REQUEST,data=serializer.errors)
    

class MyView(APIView):
    permission_classes = [IsAuthenticated , IsVerifiedUser]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
        
