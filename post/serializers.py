# post/serializers.py
from rest_framework import serializers
from .models import Post, Category
import json


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    thumbnail_url = serializers.SerializerMethodField()

    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        write_only=True,
        child=serializers.IntegerField(),
        required=False
    )

    class Meta:
        model = Post
        fields = [
            'author',
            'title',
            'body',
            'excerpt',
            'tags',
            'categories',
            'category_ids',
            'thumbnail',
            'thumbnail_url',
            'slug',
            'is_published',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'slug',
            'created_at',
            'updated_at',
            'is_deleted',
            'excerpt',
        ]

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            return request.build_absolute_uri(obj.thumbnail.url) if request else obj.thumbnail.url
        return None

    def create(self, validated_data):
        """Assign author and attach categories."""
        category_ids = validated_data.pop('categories', [])
        user = self.context['request'].user

        post = Post.objects.create(author=user, **validated_data)

        if category_ids:
            post.categories.set(Category.objects.filter(id__in=category_ids))

        return post

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('categories', None)
        instance = super().update(instance, validated_data)

        if category_ids is not None:
            instance.categories.set(Category.objects.filter(id__in=category_ids))

        return instance
    
    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        # Request raw data for categories
        raw = self.context["request"].data.get("categories")

        if raw:
            try:
                data["categories"] = json.loads(raw)
            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    {"categories": "Categories must be a JSON list like [1,2,3]."}
                )

        return data
