# post/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from user_management.models import UserModel
import uuid
import os
import re

def post_upload_path(instance, filename):
    """
    Upload path: /media/{user-slug}/posts/{filename}
    """
    user_slug = getattr(instance.author, "slug", instance.author.username)
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(f"{user_slug}/posts/", filename)


class PostManager(models.Manager):
    """Custom manager for soft delete filtering."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE ,related_name='posts')
    title = models.CharField(max_length=250)
    body = models.TextField()  # raw HTML
    excerpt = models.TextField(blank=True)  # text-only summary
    tags = models.JSONField(default=list, blank=True)

    categories = models.ManyToManyField(Category, blank=True)

    thumbnail = models.ImageField(upload_to=post_upload_path)
    slug = models.SlugField(unique=True, blank=True)

    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostManager()
    all_objects = models.Manager()

    def generate_excerpt(self):
        """Strip HTML tags & take first 40 words."""
        clean_text = re.sub('<[^<]+?>', '', self.body)
        words = clean_text.split()
        return " ".join(words[:40]) + ("..." if len(words) > 40 else "")

    def save(self, *args, **kwargs):
        # Slug
        if not self.slug:
            base_slug = slugify(self.title)
            unique_suffix = uuid.uuid4().hex[:6]
            self.slug = f"{base_slug}-{unique_suffix}"

        # Auto excerpt
        self.excerpt = self.generate_excerpt()

        super().save(*args, **kwargs)

    def delete(self):
        """Soft delete."""
        self.is_published = False
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return f"{self.title} ({'Deleted' if self.is_deleted else 'Active'})"
