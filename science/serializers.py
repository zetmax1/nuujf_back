from rest_framework import serializers
from .models import ScienceIndex, ResearchArea, ResearchDetail

class ScienceIndexSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ScienceIndex
        fields = [
            'id', 'title', 'description', 
            'stat1_label', 'stat1_value',
            'stat2_label', 'stat2_value',
            'stat3_label', 'stat3_value',
            'stat4_label', 'stat4_value',
            'cover_image_url'
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.file.url)
            return obj.cover_image.file.url
        return None


class ResearchDetailSerializer(serializers.ModelSerializer):
    main_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ResearchDetail
        fields = [
            'id', 'subtitle', 'content', 'main_image_url',
            'stat1_label', 'stat1_value',
            'stat2_label', 'stat2_value',
            'stat3_label', 'stat3_value'
        ]

    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.file.url)
            return obj.main_image.file.url
        return None


class ResearchAreaSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    
    class Meta:
        model = ResearchArea
        fields = ['id', 'title', 'slug', 'description', 'order', 'is_active', 'details']

    def get_details(self, obj):
        # Use getattr with default None to safely check for the related object
        detail_obj = getattr(obj, 'details', None)
        if detail_obj:
            return ResearchDetailSerializer(detail_obj, context=self.context).data
        return None
