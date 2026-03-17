from rest_framework import serializers
from .models import InformationSystem

class InformationSystemSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = InformationSystem
        fields = ['id', 'name', 'link', 'order', 'short_description', 'icon_url']

    def get_icon_url(self, obj):
        if obj.icon:
            return obj.icon.file.url
        return None
