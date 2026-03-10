import os
import re
import magic
from rest_framework import serializers
from django.utils.timesince import timesince
from django.core.validators import FileExtensionValidator
from .models import Vacancy, VacancyApplication


# ============================================
# SECURITY: File validation constants
# ============================================

# Allowed file extensions
ALLOWED_EXTENSIONS = ['pdf']

# Allowed MIME types (real file type check, not just extension)
ALLOWED_MIME_TYPES = {
    'application/pdf',
}

# Max file size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Phone regex: Uzbek phone format
PHONE_REGEX = re.compile(r'^\+?998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$')


class VacancyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for vacancy listing"""
    employment_type_display = serializers.CharField(
        source='get_employment_type_display', read_only=True
    )
    category_display = serializers.CharField(
        source='get_category_display', read_only=True
    )
    time_ago = serializers.SerializerMethodField()
    salary_range = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            'id', 'title', 'department',
            'employment_type', 'employment_type_display',
            'category', 'category_display',
            'salary_min', 'salary_max', 'salary_range',
            'is_active', 'created_at', 'time_ago',
        ]

    def get_time_ago(self, obj):
        return timesince(obj.created_at) + " oldin"

    def get_salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_min:,} - {obj.salary_max:,} so'm"
        elif obj.salary_min:
            return f"{obj.salary_min:,} so'm dan"
        elif obj.salary_max:
            return f"{obj.salary_max:,} so'm gacha"
        return "Kelishiladi"


class VacancyDetailSerializer(serializers.ModelSerializer):
    """Full serializer for vacancy detail"""
    employment_type_display = serializers.CharField(
        source='get_employment_type_display', read_only=True
    )
    category_display = serializers.CharField(
        source='get_category_display', read_only=True
    )
    time_ago = serializers.SerializerMethodField()
    salary_range = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            'id', 'title', 'department',
            'employment_type', 'employment_type_display',
            'category', 'category_display',
            'salary_min', 'salary_max', 'salary_range',
            'description', 'requirements',
            'is_active', 'created_at', 'time_ago',
            'applications_count',
        ]

    def get_time_ago(self, obj):
        return timesince(obj.created_at) + " oldin"

    def get_salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_min:,} - {obj.salary_max:,} so'm"
        elif obj.salary_min:
            return f"{obj.salary_min:,} so'm dan"
        elif obj.salary_max:
            return f"{obj.salary_max:,} so'm gacha"
        return "Kelishiladi"

    def get_applications_count(self, obj):
        return obj.applications.count()


class VacancyApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for submitting vacancy applications.
    
    Security layers:
    1. File extension validation (only PDF, DOC, DOCX)
    2. MIME type validation (checks real file content, not just extension)
    3. File size limit (max 5 MB)
    4. Phone number format validation
    5. Input length limits via model constraints
    """

    resume = serializers.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text="Faqat PDF format. Maksimum 5 MB.",
    )

    class Meta:
        model = VacancyApplication
        fields = [
            'id', 'vacancy', 'full_name', 'phone',
            'email', 'resume', 'cover_letter', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_phone(self, value):
        """Validate Uzbek phone number format"""
        cleaned = value.strip()
        if not PHONE_REGEX.match(cleaned):
            raise serializers.ValidationError(
                "Telefon raqam noto'g'ri formatda. Masalan: +998 90 123 45 67"
            )
        return cleaned

    def validate_full_name(self, value):
        """Sanitize name — strip HTML and limit length"""
        cleaned = re.sub(r'<[^>]+>', '', value).strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError("Ism juda qisqa.")
        if len(cleaned) > 255:
            raise serializers.ValidationError("Ism juda uzun.")
        return cleaned

    def validate_cover_letter(self, value):
        """Sanitize cover letter — strip HTML tags"""
        if value:
            cleaned = re.sub(r'<[^>]+>', '', value).strip()
            if len(cleaned) > 2000:
                raise serializers.ValidationError("Xabar 2000 belgidan oshmasligi kerak.")
            return cleaned
        return value

    def validate_resume(self, value):
        """
        Deep PDF file validation:
        1. Check file size
        2. Check real MIME type via python-magic
        3. Parse PDF to test validity
        4. Scan for malicious embedded scripts
        """
        # 1. Check file size
        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"Fayl hajmi juda katta. Maksimum: {MAX_FILE_SIZE // (1024 * 1024)} MB"
            )

        # 2. Check extension early
        ext = os.path.splitext(value.name)[1].lower().lstrip('.')
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Faqat PDF formati qabul qilinadi."
            )

        # Read file completely to scan bytes
        value.seek(0)
        raw_bytes = value.read()
        value.seek(0)

        # 3. Check real MIME type and magic bytes
        try:
            mime = magic.from_buffer(raw_bytes, mime=True)
            if mime not in ALLOWED_MIME_TYPES:
                raise serializers.ValidationError(
                    f"Fayl turi ruxsat etilmagan ({mime}). Faqat PDF hujjat ruxsat etilgan."
                )
        except ImportError:
            pass

        if not raw_bytes.startswith(b"%PDF-"):
            raise serializers.ValidationError("Fayl yaroqli PDF emas.")

        # 4. Try to parse using pypdf
        from pypdf import PdfReader
        from io import BytesIO
        try:
            reader = PdfReader(BytesIO(raw_bytes))
            _ = len(reader.pages)  # force parse
        except Exception:
            raise serializers.ValidationError("PDF faylni o'qib bo'lmadi (shikastlangan).")

        # 5. Scan for embedded scripts / JavaScript inside PDF
        suspicious_patterns = [
            b"/JavaScript",
            b"/JS",
            b"/AA",          # auto-action
            b"/OpenAction",
            b"/Launch",
            b"/EmbeddedFile",
            b"<?php",
            b"<script",
        ]
        raw_lower = raw_bytes.lower()
        for pattern in suspicious_patterns:
            if pattern in raw_lower:
                raise serializers.ValidationError("Faylda shubhali (zararli) matn qismlari aniqlandi.")

        return value
