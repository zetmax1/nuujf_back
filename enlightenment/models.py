from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index


class AchievementSection(index.Indexed, models.Model):
    """
    Ordered content blocks for the Achievements page ("Yuksak marralar").
    Each section has a title, rich-text content, and optional cover image.
    """

    title = models.CharField(
        max_length=255,
        help_text="Bo'lim sarlavhasi"
    )
    content = RichTextField(
        blank=True,
        help_text="Bo'lim mazmuni"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Bo'lim uchun rasm"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami (0 = birinchi)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi? (O'chirilsa saytda ko'rinmaydi)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    search_fields = [
        index.SearchField('title'),
        index.FilterField('is_active'),
    ]

    panels = [
        MultiFieldPanel([
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('content_uz'),
            FieldPanel('content_ru'),
            FieldPanel('content_en'),
        ], heading="Mazmun (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Yutuq bo'limi"
        verbose_name_plural = "Yutuqlar"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class EnlightenmentSection(index.Indexed, models.Model):
    """
    Ordered content blocks for the Enlightenment page ("Ma'rifiy muhit").
    Each section has a title, rich-text content, and optional cover image.
    """

    title = models.CharField(
        max_length=255,
        help_text="Bo'lim sarlavhasi"
    )
    content = RichTextField(
        blank=True,
        help_text="Bo'lim mazmuni"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Bo'lim uchun rasm"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami (0 = birinchi)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi? (O'chirilsa saytda ko'rinmaydi)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    search_fields = [
        index.SearchField('title'),
        index.FilterField('is_active'),
    ]

    panels = [
        MultiFieldPanel([
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('content_uz'),
            FieldPanel('content_ru'),
            FieldPanel('content_en'),
        ], heading="Mazmun (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Ma'rifat bo'limi"
        verbose_name_plural = "Ma'rifat bo'limlari"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Club(index.Indexed, models.Model):
    """
    Active clubs and circles ("Faol Klub va To'garaklar").
    Each club has its own detail page accessible via slug.
    Examples: Zakovat Klub, Teatr Studiyasi, Kitobxonlar Klubi, Yosh Volontyorlar.
    """

    name = models.CharField(
        max_length=255,
        help_text="Klub nomi, masalan: Zakovat Klub"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    description = models.TextField(
        blank=True,
        help_text="Qisqacha tavsif (kartochka uchun)"
    )
    content = RichTextField(
        blank=True,
        help_text="To'liq mazmun (batafsil sahifa uchun)"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Klub uchun muqova rasm"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami (0 = birinchi)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi? (O'chirilsa saytda ko'rinmaydi)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    search_fields = [
        index.SearchField('name'),
        index.FilterField('is_active'),
    ]

    panels = [
        MultiFieldPanel([
            FieldPanel('name_uz'),
            FieldPanel('name_ru'),
            FieldPanel('name_en'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
        ], heading="Qisqacha tavsif (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('content_uz'),
            FieldPanel('content_ru'),
            FieldPanel('content_en'),
        ], heading="To'liq mazmun (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Klub"
        verbose_name_plural = "Klublar"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = 'klub'
            slug = base_slug
            counter = 1
            while Club.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

