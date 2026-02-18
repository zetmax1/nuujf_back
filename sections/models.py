from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable
from wagtail.search import index


class Leader(index.Indexed, models.Model):
    """University leadership — Rector, Pro-rectors, etc."""

    full_name = models.CharField(
        max_length=255,
        help_text="To'liq ism-sharif, masalan: Abdullayev Sherzod Nematovich"
    )

    position = models.CharField(
        max_length=255,
        help_text="Lavozim, masalan: Rektor, Ilmiy ishlar bo'yicha prorektor"
    )

    academic_degree = models.CharField(
        max_length=255,
        blank=True,
        help_text="Ilmiy daraja, masalan: Texnika fanlari doktori, Professor"
    )

    email = models.EmailField(
        help_text="Elektron pochta manzili"
    )

    phone = models.CharField(
        max_length=50,
        help_text="Telefon raqam"
    )

    reception_days = models.CharField(
        max_length=255,
        blank=True,
        help_text="Qabul kunlari, masalan: Dushanba-Juma 14:00-16:00"
    )

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Rahbar surati"
    )

    bio = RichTextField(
        blank=True,
        help_text="Biografiya — qisqacha ma'lumot"
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami (0 = birinchi). Rektor = 0, prorektor = 1, 2, ..."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi? (O'chirilsa saytda ko'rinmaydi)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Wagtail search index
    search_fields = [
        index.SearchField('full_name'),
        index.SearchField('position'),
        index.FilterField('is_active'),
    ]

    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('full_name'),
            FieldPanel('position'),
            FieldPanel('academic_degree'),
            FieldPanel('image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone'),
            FieldPanel('reception_days'),
        ], heading="Aloqa ma'lumotlari"),
        FieldPanel('bio'),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Rahbar"
        verbose_name_plural = "Rahbariyat"
        ordering = ['order', 'full_name']

    def __str__(self):
        return f"{self.full_name} — {self.position}"


class StructureSection(index.Indexed, ClusterableModel):
    """
    University organizational structure — hierarchical sections.
    Top-level sections (parent=null) are "big sections" (e.g. Rector, Vice-Rectors).
    Child sections are "sub-sections" (e.g. departments, centres).
    """

    name = models.CharField(
        max_length=255,
        help_text="Bo'lim nomi, masalan: Ilmiy ishlar bo'yicha prorektor"
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL uchun identifikator (avtomatik to'ldiriladi)"
    )

    description = RichTextField(
        blank=True,
        help_text="Bo'lim haqida qo'shimcha ma'lumot"
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ikonka CSS klassi yoki emoji (masalan: 🏛️ yoki fa-university)"
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Yuqori bo'lim (bo'sh = asosiy bo'lim)"
    )

    leader = models.ForeignKey(
        Leader,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='structure_sections',
        help_text="Bo'lim rahbari (Leader modelidan)"
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

    # Wagtail search index
    search_fields = [
        index.SearchField('name'),
        index.FilterField('is_active'),
    ]

    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('icon'),
            FieldPanel('parent'),
            FieldPanel('leader'),
        ], heading="Asosiy ma'lumotlar"),
        FieldPanel('description'),
        InlinePanel('members', label="Bo'lim a'zolari"),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Tuzilma bo'limi"
        verbose_name_plural = "Tuzilma"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class SectionMember(Orderable, models.Model):
    """
    Additional participants/members of a structure section.
    For people who aren't Leaders but belong to a section.
    """

    section = ParentalKey(
        StructureSection,
        on_delete=models.CASCADE,
        related_name='members',
        help_text="Tegishli bo'lim"
    )

    full_name = models.CharField(
        max_length=255,
        help_text="To'liq ism-sharif"
    )

    position = models.CharField(
        max_length=255,
        help_text="Lavozim"
    )

    email = models.EmailField(
        blank=True,
        help_text="Elektron pochta manzili"
    )

    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Telefon raqam"
    )

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="A'zo surati"
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami"
    )

    panels = [
        FieldPanel('full_name'),
        FieldPanel('position'),
        FieldPanel('email'),
        FieldPanel('phone'),
        FieldPanel('image'),
        FieldPanel('order'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Bo'lim a'zosi"
        verbose_name_plural = "Bo'lim a'zolari"
        ordering = ['order', 'full_name']

    def __str__(self):
        return f"{self.full_name} — {self.position}"
