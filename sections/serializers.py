from rest_framework import serializers
from .models import Leader, StructureSection, SectionMember


class LeaderSerializer(serializers.ModelSerializer):
    """Serializer for university leadership"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Leader
        fields = [
            'id', 'full_name', 'position', 'academic_degree',
            'email', 'phone', 'reception_days',
            'image_url', 'bio', 'order',
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            url = obj.image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class SectionMemberSerializer(serializers.ModelSerializer):
    """Serializer for section members/participants"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SectionMember
        fields = [
            'id', 'full_name', 'position',
            'email', 'phone', 'image_url', 'order',
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            url = obj.image.file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class StructureSectionSerializer(serializers.ModelSerializer):
    """
    Serializer for university structure sections.
    Includes nested leader, members, and children.
    """
    leader = LeaderSerializer(read_only=True)
    members = SectionMemberSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = StructureSection
        fields = [
            'id', 'name', 'slug', 'icon',
            'order', 'leader', 'members', 'children',
        ]

    def get_children(self, obj):
        """Recursively serialize child sections."""
        children = obj.children.filter(is_active=True).order_by('order', 'name')
        return StructureSectionSerializer(
            children, many=True, context=self.context
        ).data


class StructureSectionDetailSerializer(serializers.ModelSerializer):
    """
    Full detail serializer for a single section — includes description.
    """
    leader = LeaderSerializer(read_only=True)
    members = SectionMemberSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = StructureSection
        fields = [
            'id', 'name', 'slug', 'icon', 'description',
            'order', 'leader', 'members', 'children',
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('order', 'name')
        return StructureSectionSerializer(
            children, many=True, context=self.context
        ).data
