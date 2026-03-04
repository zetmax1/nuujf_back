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
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
            FieldPanel('icon'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
        ], heading="Tavsif (3 tilda)"),
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
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Hamkorlik haqida muqova rasm (banner)"
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
            FieldPanel('name_uz'),
            FieldPanel('name_ru'),
            FieldPanel('name_en'),
            FieldPanel('collaboration_type'),
            FieldPanel('country_uz'),
            FieldPanel('country_ru'),
            FieldPanel('country_en'),
            FieldPanel('website'),
            FieldPanel('logo'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
        ], heading="Tavsif (3 tilda)"),
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
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
            FieldPanel('collaboration_type'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('content_uz'),
            FieldPanel('content_ru'),
            FieldPanel('content_en'),
        ], heading="Mazmun (3 tilda)"),
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


class CollaborationPage(index.Indexed, models.Model):
    """
    Rich content page within a collaboration type.
    Supports unlimited nesting via self-referencing parent FK.
    Examples: "Talabalar almashinuvi", "Erasmus+ grantlar", "Study in Uzbekistan".
    """

    title = models.CharField(
        max_length=255,
        help_text="Sahifa sarlavhasi"
    )
    slug = models.SlugField(
        max_length=255,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    collaboration_type = models.ForeignKey(
        CollaborationType,
        on_delete=models.CASCADE,
        related_name='pages',
        help_text="Tegishli hamkorlik turi"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Yuqori sahifa (bo'sh = hamkorlik turining to'g'ridan-to'g'ri bolasi)"
    )
    content = RichTextField(
        blank=True,
        help_text="Sahifa mazmuni"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Sahifa uchun muqova rasm"
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
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
            FieldPanel('collaboration_type'),
            FieldPanel('parent'),
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
        verbose_name = "Hamkorlik sahifasi"
        verbose_name_plural = "Hamkorlik sahifalari"
        ordering = ['order', 'title']
        unique_together = ['collaboration_type', 'slug']

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        if self.parent and self.parent.collaboration_type_id != self.collaboration_type_id:
            raise ValidationError({
                'parent': "Yuqori sahifa shu hamkorlik turiga tegishli bo'lishi kerak. "
                          f"Tanlangan sahifa '{self.parent.collaboration_type.title}' turiga tegishli."
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'sahifa'
            slug = base_slug
            counter = 1
            while (CollaborationPage.objects
                   .filter(collaboration_type=self.collaboration_type, slug=slug)
                   .exclude(pk=self.pk)
                   .exists()):
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_breadcrumbs(self):
        """Build breadcrumb trail from this page up to the collaboration type."""
        crumbs = []
        current = self
        while current is not None:
            crumbs.insert(0, {
                'title': current.title,
                'slug': current.slug,
            })
            current = current.parent
        # Add collaboration type as the first crumb
        crumbs.insert(0, {
            'title': self.collaboration_type.title,
            'slug': self.collaboration_type.slug,
        })
        return crumbs

    def __str__(self):
        return f"{self.collaboration_type.title} → {self.title}"

