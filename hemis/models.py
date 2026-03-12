from django.db import models
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

class HemisStatistic(models.Model):
    students_count = models.IntegerField(default=0, verbose_name="Jami talabalar soni")
    teachers_count = models.IntegerField(default=0, verbose_name="Jami o'qituvchilar soni")
    efficiency = models.IntegerField(default=45, verbose_name="Natijadorlik (%)")
    directions_count = models.IntegerField(default=9, verbose_name="Yo'nalishlar soni")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Oxirgi yangilanish vaqti")

    panels = [
        MultiFieldPanel([
            FieldPanel('students_count', read_only=True),
            FieldPanel('teachers_count', read_only=True),
        ], heading="Avtomatik (HEMIS API)"),
        MultiFieldPanel([
            FieldPanel('efficiency'),
            FieldPanel('directions_count'),
        ], heading="Qo'lda kiritiladigan (Manual)"),
    ]

    class Meta:
        verbose_name = "Hemis Statistikasi"
        verbose_name_plural = "Hemis Statistikalari"

    def __str__(self):
        if self.updated_at:
            return f"Statistika ({self.updated_at.strftime('%Y-%m-%d %H:%M')})"
        return "Yangi Statistika"

    def clean(self):
        super().clean()
        if not self.pk and HemisStatistic.objects.exists():
            raise ValidationError("Faqat bitta Hemis Statistikasi (singleton) bo'lishi mumkin. Iltimos, mavjud bo'lganini tahrirlang yoki uni o'chirib qayta yarating.")

    def save(self, *args, **kwargs):
        # Enforce singleton pattern gracefully in backend
        if not self.pk and HemisStatistic.objects.exists():
            # Update the existing one instead of failing silently to Wagtail's audit log
            existing = HemisStatistic.objects.first()
            self.pk = existing.pk
        return super(HemisStatistic, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj
