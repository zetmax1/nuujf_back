from django import forms
from django.db import models
from django.utils import timezone
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index


class Vacancy(index.Indexed, models.Model):
    """University staff vacancy listing"""

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', "To'liq stavka"),
        ('part_time', "Yarim stavka"),
    ]

    CATEGORY_CHOICES = [
        ('academic', 'Pedagogik'),
        ('technical', 'Texnik'),
        ('admin', "Ma'muriy"),
    ]

    title = models.CharField(
        max_length=255,
        help_text="Vakansiya nomi, masalan: Katta O'qituvchi"
    )

    department = models.CharField(
        max_length=255,
        help_text="Bo'lim yoki kafedra nomi"
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        help_text="Ish turi"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='academic',
        help_text="Vakansiya toifasi"
    )

    salary_min = models.PositiveIntegerField(
        help_text="Minimal ish haqi (so'm)",
        default=0
    )

    salary_max = models.PositiveIntegerField(
        help_text="Maksimal ish haqi (so'm)",
        default=0
    )

    description = RichTextField(
        blank=True,
        help_text="Vakansiya haqida to'liq ma'lumot"
    )

    requirements = RichTextField(
        blank=True,
        help_text="Talablar"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Vakansiya faolmi?"
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Yaratilgan sana"
    )

    updated_at = models.DateTimeField(auto_now=True)

    # Wagtail search index
    search_fields = [
        index.SearchField('title'),
        index.SearchField('department'),
        index.FilterField('category'),
        index.FilterField('is_active'),
    ]

    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
            FieldPanel('department_uz'),
            FieldPanel('department_ru'),
            FieldPanel('department_en'),
            FieldPanel('category'),
            FieldPanel('employment_type'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('salary_min', widget=forms.NumberInput(attrs={'step': '1', 'min': '0'})),
            FieldPanel('salary_max', widget=forms.NumberInput(attrs={'step': '1', 'min': '0'})),
        ], heading="Ish haqi"),
        MultiFieldPanel([
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
        ], heading="Tavsif (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('requirements_uz'),
            FieldPanel('requirements_ru'),
            FieldPanel('requirements_en'),
        ], heading="Talablar (3 tilda)"),
        FieldPanel('is_active'),
    ]

    class Meta:
        verbose_name = "Vakansiya"
        verbose_name_plural = "Vakansiyalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.department}"


class VacancyApplication(models.Model):
    """Application submitted for a vacancy"""

    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="Qaysi vakansiyaga ariza"
    )

    full_name = models.CharField(
        max_length=255,
        help_text="To'liq ism-sharif"
    )

    phone = models.CharField(
        max_length=20,
        help_text="Telefon raqam"
    )

    email = models.EmailField(
        blank=True,
        help_text="Elektron pochta (ixtiyoriy)"
    )

    resume = models.FileField(
        upload_to='vacancy_resumes/%Y/%m/',
        help_text="Ma'lumotnoma fayl (PDF, DOC, DOCX)"
    )

    cover_letter = models.TextField(
        blank=True,
        help_text="Qo'shimcha xabar (ixtiyoriy)"
    )

    is_read = models.BooleanField(
        default=False,
        help_text="Admin ko'rganmi?"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ariza"
        verbose_name_plural = "Arizalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} → {self.vacancy.title}"
