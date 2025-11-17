from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    thumbnail_url = serializers.SerializerMethodField()
    is_deleted = serializers.BooleanField(read_only=True)
    slug = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            'author',
            'title',
            'body',
            'tags',
            'thumbnail',
            'thumbnail_url',
            'slug',
            'is_published',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'is_deleted']

    def get_thumbnail_url(self, obj):
        """
        Returns absolute URL for thumbnail if available.
        """
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            return request.build_absolute_uri(obj.thumbnail.url) if request else obj.thumbnail.url
        return None
    

    def create(self, validated_data):
        """
        Automatically assign logged-in user as author.
        """
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)
