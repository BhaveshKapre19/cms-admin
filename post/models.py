from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from user_management.models import UserModel
import uuid
import os


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
        """Show all posts, including deleted."""
        return super().get_queryset()


class Post(models.Model):
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    body = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    thumbnail = models.ImageField(upload_to=post_upload_path)
    slug = models.SlugField(unique=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Managers
    objects = PostManager()
    all_objects = models.Manager()  # default manager to see all

    def save(self, *args, **kwargs):
        # Auto-generate unique slug
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """Soft delete instead of permanent delete."""
        self.is_published = False
        self.is_deleted = True
        self.save()

    def restore(self):
        """Restore a soft-deleted post."""
        self.is_deleted = False
        self.save()

    def __str__(self):
        return f"{self.title} ({'Deleted' if self.is_deleted else 'Active'})"



# class PostViewCount(models.Model):
#     post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='views')
#     ip_addr = models.GenericIPAddressField()
#     user_agent = models.CharField(max_length=255)
#     viewed_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         managed = True
#         verbose_name = 'postview'
#         verbose_name_plural = 'postviews'
#         unique_together = ('post','ip_addr','user_agent')

