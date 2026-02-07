from rest_framework import serializers
from .models import NewsPage, NewsImage


class NewsImageSerializer(serializers.ModelSerializer):
    """Serializer for gallery images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsImage
        fields = ['id', 'image_url', 'caption', 'sort_order']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.file.url
        return None


class NewsPageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for news listing"""
    cover_image_url = serializers.SerializerMethodField()
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    
    class Meta:
        model = NewsPage
        fields = [
            'id', 'title', 'slug', 'post_type', 'post_type_display',
            'excerpt', 'cover_image_url', 'published_date',
            'is_pinned', 'views_count'
        ]
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.file.url
        return None


class NewsPageDetailSerializer(serializers.ModelSerializer):
    """Full serializer for news detail"""
    gallery_images = NewsImageSerializer(many=True, read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    
    class Meta:
        model = NewsPage
        fields = [
            'id', 'title', 'slug', 'post_type', 'post_type_display',
            'excerpt', 'content', 'cover_image_url', 'published_date',
            'is_pinned', 'views_count', 'gallery_images',
            'synced_from_telegram'
        ]
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.file.url
        return None
