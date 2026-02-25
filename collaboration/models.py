from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index


class CollaborationType(index.Indexed, models.Model):
    """
    Category of collaboration — e.g. "Xalqaro hamkor tashkilotlar",
    "Almashinuv dasturlari", "Erasmus+ loyihalar".
    Groups related partners and projects together.
    """

    title = models.CharField(
        max_length=255,
        help_text="Hamkorlik turi nomi, masalan: Xalqaro hamkor tashkilotlar"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    description = RichTextField(
        blank=True,
        help_text="Hamkorlik turi haqida umumiy ma'lumot"
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ikonka CSS klassi yoki emoji (masalan: 🌍 yoki fa-globe)"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Hamkorlik turi uchun muqova rasm"
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

    # Wagtail search
    search_fields = [
        index.SearchField('title'),
        index.FilterField('is_active'),
    ]

    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('icon'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        FieldPanel('description'),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Hamkorlik turi"
        verbose_name_plural = "Hamkorlik turlari"
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'hamkorlik-turi'
            slug = base_slug
            counter = 1
            while CollaborationType.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PartnerOrganization(index.Indexed, models.Model):
    """
    International partner institution/organization.
    Can belong to a collaboration type and be grouped by country.
    """

    name = models.CharField(
        max_length=255,
        help_text="Hamkor tashkilot nomi"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    collaboration_type = models.ForeignKey(
        CollaborationType,
        on_delete=models.CASCADE,
        related_name='partners',
        help_text="Hamkorlik turi"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Davlat nomi (masalan: South Korea, Germany)"
    )
    website = models.URLField(
        blank=True,
        help_text="Hamkor tashkilotning veb-sayti"
    )
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Hamkor tashkilot logotipi"
    )
    description = RichTextField(
        blank=True,
        help_text="Hamkor tashkilot haqida batafsil ma'lumot"
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

    # Wagtail search
    search_fields = [
        index.SearchField('name'),
        index.SearchField('country'),
        index.FilterField('is_active'),
        index.FilterField('collaboration_type'),
    ]

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('collaboration_type'),
            FieldPanel('country'),
            FieldPanel('website'),
            FieldPanel('logo'),
        ], heading="Asosiy ma'lumotlar"),
        FieldPanel('description'),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Hamkor tashkilot"
        verbose_name_plural = "Hamkor tashkilotlar"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = 'hamkor'
            slug = base_slug
            counter = 1
            while PartnerOrganization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CollaborationProject(index.Indexed, models.Model):
    """
    Specific collaboration project or program — e.g. Erasmus+ grant,
    exchange program, joint research project.
    """

    title = models.CharField(
        max_length=255,
        help_text="Loyiha sarlavhasi"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    collaboration_type = models.ForeignKey(
        CollaborationType,
        on_delete=models.CASCADE,
        related_name='projects',
        help_text="Hamkorlik turi"
    )
    content = RichTextField(
        blank=True,
        help_text="Loyiha haqida batafsil ma'lumot"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Loyiha uchun muqova rasm"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Loyiha boshlanish sanasi"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Loyiha tugash sanasi"
    )
    partners = models.ManyToManyField(
        PartnerOrganization,
        blank=True,
        related_name='projects',
        help_text="Loyihada ishtirok etuvchi hamkor tashkilotlar"
    )
    external_link = models.URLField(
        blank=True,
        help_text="Tashqi loyiha sahifasiga havola"
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

    # Wagtail search
    search_fields = [
        index.SearchField('title'),
        index.FilterField('is_active'),
        index.FilterField('collaboration_type'),
    ]

    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('collaboration_type'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        FieldPanel('content'),
        MultiFieldPanel([
            FieldPanel('start_date'),
            FieldPanel('end_date'),
            FieldPanel('external_link'),
        ], heading="Qo'shimcha ma'lumotlar"),
        FieldPanel('partners'),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Hamkorlik loyihasi"
        verbose_name_plural = "Hamkorlik loyihalari"
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'loyiha'
            slug = base_slug
            counter = 1
            while CollaborationProject.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
