from rest_framework import serializers
from .models import HemisStatistic

class HemisStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = HemisStatistic
        fields = ['students_count', 'teachers_count', 'efficiency', 'directions_count', 'updated_at']
