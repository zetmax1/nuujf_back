import re
from rest_framework import serializers
from .models import Appeal


# Phone regex: Uzbek phone format
PHONE_REGEX = re.compile(r'^\+?998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$')


class AppealCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for submitting public appeals to the director.

    Security layers:
    1. Full name sanitization (HTML stripping, length check)
    2. Phone number format validation (Uzbek format)
    3. Message sanitization (HTML stripping, min/max length)
    4. Terms acceptance validation (must be True)
    5. Rate limiting handled at view level
    """

    class Meta:
        model = Appeal
        fields = [
            'id', 'full_name', 'email', 'department',
            'group_number', 'phone', 'message',
            'terms_accepted', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_full_name(self, value):
        """Sanitize name — strip HTML and validate length."""
        cleaned = re.sub(r'<[^>]+>', '', value).strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError("Ism juda qisqa (kamida 3 belgi).")
        if len(cleaned) > 255:
            raise serializers.ValidationError("Ism juda uzun.")
        return cleaned

    def validate_phone(self, value):
        """Validate Uzbek phone number format."""
        cleaned = value.strip()
        if not PHONE_REGEX.match(cleaned):
            raise serializers.ValidationError(
                "Telefon raqam noto'g'ri formatda. Masalan: +998 90 123 45 67"
            )
        return cleaned

    def validate_department(self, value):
        """Sanitize department — strip HTML."""
        cleaned = re.sub(r'<[^>]+>', '', value).strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError("Fakultet/bo'lim nomi juda qisqa.")
        if len(cleaned) > 255:
            raise serializers.ValidationError("Fakultet/bo'lim nomi juda uzun.")
        return cleaned

    def validate_message(self, value):
        """Sanitize appeal text — strip HTML, enforce length limits."""
        cleaned = re.sub(r'<[^>]+>', '', value).strip()
        if len(cleaned) < 10:
            raise serializers.ValidationError(
                "Murojaat matni juda qisqa (kamida 10 belgi)."
            )
        if len(cleaned) > 5000:
            raise serializers.ValidationError(
                "Murojaat matni 5000 belgidan oshmasligi kerak."
            )
        return cleaned

    def validate_group_number(self, value):
        """Sanitize group number — strip HTML."""
        if value:
            cleaned = re.sub(r'<[^>]+>', '', value).strip()
            if len(cleaned) > 50:
                raise serializers.ValidationError("Guruh raqami juda uzun.")
            return cleaned
        return value

    def validate_terms_accepted(self, value):
        """Terms must be accepted."""
        if not value:
            raise serializers.ValidationError(
                "Murojaat yuborish qoidalarini qabul qilishingiz shart."
            )
        return value
