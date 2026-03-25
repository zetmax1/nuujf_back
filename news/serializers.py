from rest_framework import serializers
from .models import NewsPage, NewsImage


class NewsImageSerializer(serializers.ModelSerializer):
    """Serializer for gallery images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsImage
        fields = ['id', 'image_url', 'caption', 'sort_order']
    
    def get_image_url(self, obj) -> str | None:
        if obj.image:
            request = self.context.get('request')
            url = obj.image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
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
    
    def get_cover_image_url(self, obj) -> str | None:
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
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
    
    def get_cover_image_url(self, obj) -> str | None:
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
