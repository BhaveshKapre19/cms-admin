from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.text import slugify
from django.contrib.auth.password_validation import validate_password
from .models import UserModel, EmailOtp
import random
import uuid
from .utils import send_otp_email as send_verification_email
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model


User = get_user_model()


# -------------------------------
# USER SERIALIZER
# -------------------------------
class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False, allow_null=True)
    """Serializer for reading and updating user info"""
    class Meta:
        model = UserModel
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'username',
            'bio',
            'address',
            'slug',
            'profile_pic',
            'is_verified',
            'is_active',
            'date_joined',
            'updated_at',
            'is_superuser',
        ]
        read_only_fields = ['id', 'slug', 'is_verified', 'date_joined', 'updated_at','is_superuser']
    
    def get_profile_pic(self, obj):
        request = self.context.get("request")

        if not obj.profile_pic:
            return None

        url = obj.profile_pic.url

        if request:
            return request.build_absolute_uri(url)

        # Fallback for cases where request is missing
        from django.conf import settings
        return f"{settings.MEDIA_URL}{url}".replace('//', '/')


# -------------------------------
# REGISTER SERIALIZER
# -------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    """Handles new user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ['first_name','last_name','email','password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = UserModel.objects.create_user(**validated_data, password=password)

        # Create OTP for email verification
        otp_code = str(random.randint(100000, 999999))
        EmailOtp.objects.create(user=user, email=user.email, otp=otp_code)

        # ✅ Send email
        #send_verification_email(user.email, otp_code, user.username or user.first_name)

        # (Optional) – send email (implement actual mail sending later)
        print(f"OTP for {user.email}: {otp_code}")  # For testing purpose only

        return user


# -------------------------------
# LOGIN SERIALIZER
# -------------------------------
class LoginSerializer(serializers.Serializer):
    """Handles user login using email & password"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive or deleted.")
        if not user.is_verified:
            raise serializers.ValidationError("Email not verified. Please verify your account.")

        attrs['user'] = user
        return attrs


# -------------------------------
# OTP VERIFY SERIALIZER
# -------------------------------
class EmailOtpSerializer(serializers.Serializer):
    """Verify OTP for email confirmation"""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            otp_obj = EmailOtp.objects.filter(email=email, otp=otp, is_used=False).latest('created_at')
        except EmailOtp.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP.")
        

        expiry_time = otp_obj.created_at + timedelta(minutes=10)
        if timezone.now() > expiry_time:
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        user = otp_obj.user
        user.is_verified = True
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        attrs['user'] = user
        return attrs




class ForgotPasswordRequestSerializer(serializers.Serializer):
    """ this is the forget password request"""
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.get(email=email)
        otp = str(random.randint(000000,999999))

        EmailOtp.objects.create(user=user,email=email,otp=otp)

        send_verification_email(email,otp,user.first_name or user.username,purpose="password_forget")

        return user



class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email=attrs.get('email')
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')

        try:
            otp_obj = EmailOtp.objects.filter(email=email,otp=otp,is_used=False).latest()
        except EmailOtp.DoesNotExist:
            raise serializers.ValidationError({
                "otp":"invalid otp or expired otp"
            })
        
        expiry_time = otp_obj.created_at +timedelta(minutes=10)
        if timezone.now() > expiry_time:
            raise serializers.ValidationError({"otp":"the otp is expired please request the new one"})
        
        user = otp_obj.user
        validate_password(new_password,user=user)

        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        attrs['new_password'] = new_password
        return attrs
    
    def save(self, **kwargs):
        user = self.validated_data['user']
        otp_obj = self.validated_data['otp_obj']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        otp_obj.is_used=True
        otp_obj.save(update_fields=['is_used'])

        return {"message":"the users password is reset successfully"}