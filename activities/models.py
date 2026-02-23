from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index


class ActivityCategory(index.Indexed, models.Model):
    """
    Top-level activity category — e.g. "O'quv faoliyati", "Ilmiy faoliyat".
    Groups related activity pages together.
    """

    title = models.CharField(
        max_length=255,
        help_text="Kategoriya nomi, masalan: O'quv faoliyati"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    description = RichTextField(
        blank=True,
        help_text="Kategoriya haqida umumiy ma'lumot"
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ikonka CSS klassi yoki emoji (masalan: 🎓 yoki fa-book)"
    )
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Kategoriya uchun muqova rasm"
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

    # Wagtail admin panels — slug is hidden (auto-generated)
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
        verbose_name = "Faoliyat kategoriyasi"
        verbose_name_plural = "Faoliyat kategoriyalari"
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'kategoriya'
            slug = base_slug
            counter = 1
            while ActivityCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ActivityPage(index.Indexed, models.Model):
    """
    Activity page with unlimited nesting depth.
    - parent=null → direct child of a category
    - parent=some_page → child of that page (can go infinitely deep)
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
    category = models.ForeignKey(
        ActivityCategory,
        on_delete=models.CASCADE,
        related_name='pages',
        help_text="Tegishli kategoriya"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Yuqori sahifa (bo'sh = kategoriyaning to'g'ridan-to'g'ri bolasi)"
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
        index.FilterField('category'),
    ]

    # Wagtail admin panels — slug is hidden (auto-generated)
    panels = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('category'),
            FieldPanel('parent'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        FieldPanel('content'),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Faoliyat sahifasi"
        verbose_name_plural = "Faoliyat sahifalari"
        ordering = ['order', 'title']
        unique_together = ['category', 'slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'sahifa'
            slug = base_slug
            counter = 1
            while (ActivityPage.objects
                   .filter(category=self.category, slug=slug)
                   .exclude(pk=self.pk)
                   .exists()):
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_breadcrumbs(self):
        """Build breadcrumb trail from this page up to the category."""
        crumbs = []
        current = self
        while current is not None:
            crumbs.insert(0, {
                'title': current.title,
                'slug': current.slug,
            })
            current = current.parent
        # Add category as the first crumb
        crumbs.insert(0, {
            'title': self.category.title,
            'slug': self.category.slug,
        })
        return crumbs

    def __str__(self):
        return f"{self.category.title} → {self.title}"
