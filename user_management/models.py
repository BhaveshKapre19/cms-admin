import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.text import slugify
from django.utils import timezone


# -------------------------------
# Custom User Manager
# -------------------------------
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with email and password"""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if not user.slug:
            user.slug = slugify(user.username) + "-" + str(uuid.uuid4())[:8]
        user.save(using=self._db)
        return user

    def create_superuser(self, email="admin@admin.com", password="admin", **extra_fields):
        """Create and save a superuser with default credentials"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('username', "admin")

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# -------------------------------
# Upload Path Function
# -------------------------------
def user_profile_pic_path(instance, filename):
    """Store image under /media/<slug>/<filename>"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"{instance.slug}/{filename}"


# -------------------------------
# Custom User Model
# -------------------------------
class UserModel(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)

    # Custom fields
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # username is optional since Django auto-creates one

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        """Soft delete: mark user inactive instead of deleting"""
        self.is_deleted = True
        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        """Auto-generate slug on creation"""
        if not self.slug:
            base_slug = slugify(self.username or self.email.split('@')[0])
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


# -------------------------------
# OTP Model for Email Verification
# -------------------------------
class EmailOtp(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="otp_codes")
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.email} - {self.otp}"

    class Meta:
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"
