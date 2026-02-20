from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


# All known frontend pages — admins pick from this dropdown
KNOWN_PAGES = [
    ('', '— Tanlang —'),
    ('home', 'Bosh sahifa'),
    ('about', 'Filial haqida'),
    ('leadership', 'Rahbariyat'),
    ('structure', 'Tuzilma'),
    ('vacancies', "Bo'sh ish o'rinlari"),
    ('education', "O'quv faoliyati"),
    ('faculties', 'Fakultetlar'),
    ('departments', 'Kafedralar'),
    ('science', 'Ilmiy faoliyat'),
    ('spirituality', "Ma'naviy faoliyat"),
    ('international', 'Xalqaro hamkorlik'),
    ('admission', 'Qabul'),
    ('distance-learning', "Masofaviy ta'lim"),
    ('library', 'Kutubxona'),
    ('systems', 'Elektron tizimlar'),
    ('payment', "To'lov-kontrakt"),
    ('news', 'Yangiliklar'),
    ('announcements', "E'lonlar"),
]


@register_snippet
class DynamicPage(models.Model):
    """A flexible content page created from the admin panel."""

    title = models.CharField(
        max_length=255,
        help_text="Sahifa sarlavhasi"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    body = RichTextField(
        blank=True,
        help_text="Sahifa mazmuni"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('body'),
        FieldPanel('is_active'),
    ]

    class Meta:
        verbose_name = "Dinamik sahifa"
        verbose_name_plural = "Dinamik sahifalar"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'sahifa'
            slug = base_slug
            counter = 1
            while DynamicPage.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


@register_snippet
class NavItem(ClusterableModel):
    """Top-level navigation link (e.g. 'Universitet', 'Faoliyat', 'Yangiliklar')"""

    title = models.CharField(
        max_length=200,
        help_text="Navigatsiya havola matni (masalan: Universitet)"
    )
    page_id = models.CharField(
        max_length=100,
        choices=KNOWN_PAGES,
        blank=True,
        default='',
        help_text="Mavjud sahifaga havola"
    )
    linked_page = models.ForeignKey(
        DynamicPage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nav_items',
        help_text="Dinamik sahifaga havola (yangi sahifa uchun)"
    )
    order = models.IntegerField(
        default=0,
        help_text="Tartib raqami (kichik = birinchi)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi? (o'chirilgan bo'lsa navbarda ko'rinmaydi)"
    )

    panels = [
        FieldPanel('title'),
        MultiFieldPanel([
            FieldPanel('page_id'),
            FieldPanel('linked_page'),
        ], heading="Havola turi (bittasini tanlang)"),
        FieldPanel('order'),
        FieldPanel('is_active'),
        InlinePanel('children', label="Pastki havolalar"),
    ]

    class Meta:
        verbose_name = "Navigatsiya havola"
        verbose_name_plural = "Navigatsiya havolalar"
        ordering = ['order', 'pk']

    def clean(self):
        super().clean()
        if self.page_id and self.linked_page:
            raise ValidationError(
                "Faqat bittasini tanlang: mavjud sahifa YOKI dinamik sahifa."
            )

    @property
    def link_type(self):
        if self.linked_page:
            return 'dynamic'
        return 'page'

    @property
    def resolved_page_id(self):
        if self.linked_page:
            return f"dynamic-page"
        return self.page_id

    @property
    def resolved_slug(self):
        if self.linked_page:
            return self.linked_page.slug
        return None

    def __str__(self):
        return self.title


class SubNavItem(models.Model):
    """Child navigation link within a dropdown (e.g. 'Filial haqida', 'Rahbariyat')"""

    parent = ParentalKey(
        NavItem,
        on_delete=models.CASCADE,
        related_name='children',
    )
    title = models.CharField(
        max_length=200,
        help_text="Pastki havola matni (masalan: Filial haqida)"
    )
    page_id = models.CharField(
        max_length=100,
        choices=KNOWN_PAGES,
        blank=True,
        default='',
        help_text="Mavjud sahifaga havola"
    )
    linked_page = models.ForeignKey(
        DynamicPage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_nav_items',
        help_text="Dinamik sahifaga havola (yangi sahifa uchun)"
    )
    order = models.IntegerField(
        default=0,
        help_text="Tartib raqami"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi?"
    )

    panels = [
        FieldPanel('title'),
        MultiFieldPanel([
            FieldPanel('page_id'),
            FieldPanel('linked_page'),
        ], heading="Havola turi"),
        FieldPanel('order'),
        FieldPanel('is_active'),
    ]

    class Meta:
        verbose_name = "Pastki havola"
        verbose_name_plural = "Pastki havolalar"
        ordering = ['order', 'pk']

    def clean(self):
        super().clean()
        if self.page_id and self.linked_page:
            raise ValidationError(
                "Faqat bittasini tanlang: mavjud sahifa YOKI dinamik sahifa."
            )

    @property
    def link_type(self):
        if self.linked_page:
            return 'dynamic'
        return 'page'

    @property
    def resolved_page_id(self):
        if self.linked_page:
            return 'dynamic-page'
        return self.page_id

    @property
    def resolved_slug(self):
        if self.linked_page:
            return self.linked_page.slug
        return None

    def __str__(self):
        return f"{self.parent.title} → {self.title}"
