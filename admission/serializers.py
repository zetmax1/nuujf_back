from rest_framework import serializers
from .models import AdmissionYear, AdmissionQuota


class AdmissionQuotaSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionQuota
        fields = [
            'id', 'direction_name', 'language',
            'grant_count', 'contract_count', 'total', 'order',
        ]

    def get_total(self, obj):
        return obj.grant_count + obj.contract_count


class AdmissionYearListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing years."""

    class Meta:
        model = AdmissionYear
        fields = ['id', 'title', 'is_active', 'order']


class AdmissionYearDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer — includes nested quotas."""
    quotas = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionYear
        fields = [
            'id', 'title', 'badge_text', 'hero_title', 'hero_description',
            'apply_link', 'is_active', 'order',
            'quotas',
        ]

    def get_quotas(self, obj):
        quotas = obj.quotas.all().order_by('order', 'direction_name')
        return AdmissionQuotaSerializer(quotas, many=True).data
