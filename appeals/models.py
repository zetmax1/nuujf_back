from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index


class Appeal(index.Indexed, models.Model):
    """
    Public appeal to the university director.
    Citizens / students / staff can submit appeals electronically.
    """

    full_name = models.CharField(
        max_length=255,
        help_text="To'liq ism-sharif (F.I.O)"
    )

    email = models.EmailField(
        help_text="Elektron pochta manzili"
    )

    department = models.CharField(
        max_length=255,
        help_text="Fakultet / Bo'lim / Boshqa"
    )

    group_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Guruh raqami (agar talaba bo'lsangiz)"
    )

    phone = models.CharField(
        max_length=20,
        help_text="Telefon raqam"
    )

    message = models.TextField(
        help_text="Murojaat matni"
    )

    terms_accepted = models.BooleanField(
        default=False,
        help_text="Murojaat yuborish qoidalarini qabul qilganmi?"
    )

    is_read = models.BooleanField(
        default=False,
        help_text="Admin ko'rganmi?"
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Yuborilgan sana"
    )

    # Wagtail search index
    search_fields = [
        index.SearchField('full_name'),
        index.SearchField('message'),
        index.FilterField('is_read'),
    ]

    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('full_name', read_only=True),
            FieldPanel('email', read_only=True),
            FieldPanel('department', read_only=True),
            FieldPanel('group_number', read_only=True),
            FieldPanel('phone', read_only=True),
        ], heading="Murojaat yuboruvchi ma'lumotlari"),
        MultiFieldPanel([
            FieldPanel('message', read_only=True),
        ], heading="Murojaat matni"),
        MultiFieldPanel([
            FieldPanel('terms_accepted', read_only=True),
            FieldPanel('is_read'),
        ], heading="Holat"),
    ]

    class Meta:
        verbose_name = "Direktorga murojaat"
        verbose_name_plural = "Direktorga murojaatlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.created_at:%Y-%m-%d %H:%M}"
