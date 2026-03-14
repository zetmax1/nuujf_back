from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index

class ScienceIndex(models.Model):
    """
    Main Science page content and common statistics.
    """
    title = models.CharField(max_length=255, help_text="Sarlavha (masalan: Bilim va Innovatsiya Markazi)")
    description = models.TextField(help_text="Asosiy tavsif")
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Hero section uchun background rasm"
    )
    
    # Common stats for the stats bar
    stat1_label = models.CharField(max_length=100, help_text="Statistika 1 nomi (masalan: Ilmiy xodimlar)")
    stat1_value = models.CharField(max_length=50, help_text="Statistika 1 qiymati (masalan: 150+)")
    
    stat2_label = models.CharField(max_length=100, help_text="Statistika 2 nomi")
    stat2_value = models.CharField(max_length=50, help_text="Statistika 2 qiymati")
    
    stat3_label = models.CharField(max_length=100, help_text="Statistika 3 nomi")
    stat3_value = models.CharField(max_length=50, help_text="Statistika 3 qiymati")
    
    stat4_label = models.CharField(max_length=100, help_text="Statistika 4 nomi")
    stat4_value = models.CharField(max_length=50, help_text="Statistika 4 qiymati")

    panels = [
        MultiFieldPanel([
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
            FieldPanel('cover_image'),
        ], heading="Hero Section"),
        MultiFieldPanel([
            FieldPanel('stat1_label_uz'), FieldPanel('stat1_value'),
            FieldPanel('stat1_label_ru'),
            FieldPanel('stat1_label_en'),
            FieldPanel('stat2_label_uz'), FieldPanel('stat2_value'),
            FieldPanel('stat2_label_ru'),
            FieldPanel('stat2_label_en'),
            FieldPanel('stat3_label_uz'), FieldPanel('stat3_value'),
            FieldPanel('stat3_label_ru'),
            FieldPanel('stat3_label_en'),
            FieldPanel('stat4_label_uz'), FieldPanel('stat4_value'),
            FieldPanel('stat4_label_ru'),
            FieldPanel('stat4_label_en'),
        ], heading="Statistika (Stats Bar)"),
    ]

    class Meta:
        verbose_name = "Ilmiy faoliyat asosi"
        verbose_name_plural = "Ilmiy faoliyat asosi"

    def __str__(self):
        return self.title


class ResearchArea(index.Indexed, models.Model):
    """
    Research area cards on the main Science page.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(help_text="Qisqa tavsif (karta uchun)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    search_fields = [
        index.SearchField('title'),
        index.FilterField('is_active'),
    ]

    panels = [
        MultiFieldPanel([
            FieldPanel('title_uz'),
            FieldPanel('title_ru'),
            FieldPanel('title_en'),
        ], heading="Karta ma'lumotlari"),
        MultiFieldPanel([
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
        ], heading="Tavsif"),
        FieldPanel('order'),
        FieldPanel('is_active'),
    ]

    class Meta:
        verbose_name = "Tadqiqot yo'nalishi"
        verbose_name_plural = "Tadqiqot yo'nalishlari"
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ResearchDetail(models.Model):
    """
    Detailed content for a research area.
    """
    area = models.OneToOneField(ResearchArea, on_delete=models.CASCADE, related_name='details')
    subtitle = models.CharField(max_length=255, help_text="Kichik sarlavha")
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Asosiy rasm"
    )
    content = RichTextField(help_text="Batafsil ma'lumot (Rich Text)")
    
    # Detail stats (sidebar)
    stat1_label = models.CharField(max_length=100)
    stat1_value = models.CharField(max_length=50)
    
    stat2_label = models.CharField(max_length=100)
    stat2_value = models.CharField(max_length=50)
    
    stat3_label = models.CharField(max_length=100)
    stat3_value = models.CharField(max_length=50)

    panels = [
        FieldPanel('area'),
        MultiFieldPanel([
            FieldPanel('subtitle_uz'),
            FieldPanel('subtitle_ru'),
            FieldPanel('subtitle_en'),
            FieldPanel('main_image'),
        ], heading="Header"),
        MultiFieldPanel([
            FieldPanel('content_uz'),
            FieldPanel('content_ru'),
            FieldPanel('content_en'),
        ], heading="Mazmun"),
        MultiFieldPanel([
            FieldPanel('stat1_label_uz'), FieldPanel('stat1_value'),
            FieldPanel('stat1_label_ru'),
            FieldPanel('stat1_label_en'),
            FieldPanel('stat2_label_uz'), FieldPanel('stat2_value'),
            FieldPanel('stat2_label_ru'),
            FieldPanel('stat2_label_en'),
            FieldPanel('stat3_label_uz'), FieldPanel('stat3_value'),
            FieldPanel('stat3_label_ru'),
            FieldPanel('stat3_label_en'),
        ], heading="Sidebar Statistika"),
    ]

    class Meta:
        verbose_name = "Tadqiqot tafsiloti"
        verbose_name_plural = "Tadqiqot tafsilotlari"

    def __str__(self):
        return f"{self.area.title} - Tafsilotlar"
