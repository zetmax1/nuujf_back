from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel

class InformationSystem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    link = models.URLField(verbose_name="Havola")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")
    short_description = models.TextField(verbose_name="Qisqacha tavsif")
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Ikonka (ixtiyoriy, default frontend'da ishlatiladi)"
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('link'),
        FieldPanel('order'),
        FieldPanel('short_description'),
        FieldPanel('icon'),
    ]

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Axborot tizimi"
        verbose_name_plural = "Axborot tizimlari"

    def __str__(self):
        return self.name
