from rest_framework import serializers
from .models import InformationSystem

class InformationSystemSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = InformationSystem
        fields = ['id', 'name', 'link', 'order', 'short_description', 'icon_url']

    def get_icon_url(self, obj) -> str | None:
        if obj.icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None
