from django.db import models
import os

class FileGallery(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='file_gallery/')
    size = models.PositiveIntegerField(null=True, blank=True)  # file size in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto title from filename
        if not self.title and self.file:
            self.title = os.path.basename(self.file.name)

        # Store file size automatically
        if self.file:
            self.size = self.file.size

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']
