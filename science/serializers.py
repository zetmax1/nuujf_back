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

    def get_cover_image_url(self, obj) -> str | None:
        if obj.cover_image:
            request = self.context.get('request')
            url = obj.cover_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
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

    def get_main_image_url(self, obj) -> str | None:
        if obj.main_image:
            request = self.context.get('request')
            url = obj.main_image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ResearchAreaSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    
    class Meta:
        model = ResearchArea
        fields = ['id', 'title', 'slug', 'description', 'order', 'is_active', 'details']

    def get_details(self, obj) -> list:
        details = obj.details.all().order_by('order')
        return ScienceProjectDetailItemSerializer(details, many=True, context=self.context).data
