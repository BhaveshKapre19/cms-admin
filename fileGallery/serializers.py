from rest_framework import serializers
from .models import FileGallery

class FileGallerySerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    size_human = serializers.SerializerMethodField()

    class Meta:
        model = FileGallery
        fields = [
            'id',
            'title',
            'file',
            'file_url',
            'size',
            'size_human',
            'uploaded_at',
        ]
        read_only_fields = ['uploaded_at', 'title', 'file_url', 'size_human']

    def get_file_url(self, obj):
        """Return fully-qualified URL."""
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

    def get_size_human(self, obj):
        """Convert size in bytes → KB/MB/GB string."""
        if not obj.size:
            return None

        size = obj.size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
