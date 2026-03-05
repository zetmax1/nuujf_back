from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index


class AdmissionYear(index.Indexed, models.Model):
    """
    Represents one admission year/session — e.g. "2024-2025".
    Contains the hero section text, badge, and apply link.
    """

    title = models.CharField(
        max_length=50,
        help_text="O'quv yili, masalan: 2024-2025"
    )
    badge_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Badge matni, masalan: QABUL 2024 BOSHLANDI"
    )
    hero_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Bosh sarlavha, masalan: Kelajagingizni biz bilan quring"
    )
    hero_description = models.TextField(
        blank=True,
        help_text="Bosh tavsif matni"
    )
    apply_link = models.URLField(
        max_length=500,
        default="https://my.uzbmb.uz/",
        help_text="Hujjat topshirish havolasi"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi? (Saytda ko'rinadi)"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami (0 = birinchi)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Wagtail search
    search_fields = [
        index.SearchField('title'),
        index.FilterField('is_active'),
    ]

    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
        ], heading="O'quv yili nomi (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('badge_text_uz'),
            FieldPanel('badge_text_ru'),
            FieldPanel('badge_text_en'),
        ], heading="Badge matni (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('hero_title_uz'),
            FieldPanel('hero_title_ru'),
            FieldPanel('hero_title_en'),
        ], heading="Bosh sarlavha (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('hero_description_uz'),
            FieldPanel('hero_description_ru'),
            FieldPanel('hero_description_en'),
        ], heading="Bosh tavsif (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('apply_link'),
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Qabul yili"
        verbose_name_plural = "Qabul yillari"
        ordering = ['order', '-title']

    def __str__(self):
        return self.title


class AdmissionQuota(index.Indexed, models.Model):
    """
    A row in the admission quotas table.
    """

    year = models.ForeignKey(
        AdmissionYear,
        on_delete=models.CASCADE,
        related_name='quotas',
        help_text="Tegishli qabul yili"
    )
    direction_name = models.CharField(
        max_length=255,
        help_text="Ta'lim yo'nalishi nomi"
    )
    language = models.CharField(
        max_length=100,
        help_text="Ta'lim tili, masalan: O'zbek, Rus, O'zbek/Rus"
    )
    grant_count = models.PositiveIntegerField(
        default=0,
        help_text="Grant o'rinlar soni"
    )
    contract_count = models.PositiveIntegerField(
        default=0,
        help_text="Kontrakt o'rinlar soni"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Wagtail search
    search_fields = [
        index.SearchField('direction_name'),
        index.FilterField('year'),
    ]

    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('year'),
        ], heading="Asosiy"),
        MultiFieldPanel([
            FieldPanel('direction_name_uz'),
            FieldPanel('direction_name_ru'),
            FieldPanel('direction_name_en'),
        ], heading="Yo'nalish nomi (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('language_uz'),
            FieldPanel('language_ru'),
            FieldPanel('language_en'),
        ], heading="Ta'lim tili (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('grant_count'),
            FieldPanel('contract_count'),
            FieldPanel('order'),
        ], heading="Kvota va tartib"),
    ]

    class Meta:
        verbose_name = "Qabul kvotasi"
        verbose_name_plural = "Qabul kvotalari"
        ordering = ['order', 'direction_name']

    def __str__(self):
        return f"{self.year.title} — {self.direction_name} ({self.grant_count}+{self.contract_count})"
