from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index


class Faculty(index.Indexed, models.Model):
    """University faculty."""

    name = models.CharField(
        max_length=255,
        help_text="Fakultet nomi"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    faculty_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Fakultet kodi"
    )
    short_description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Qisqacha tavsif"
    )
    description = RichTextField(
        blank=True,
        help_text="To'liq tavsif"
    )

    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Muqova rasm"
    )

    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    office_location = models.CharField(max_length=255, blank=True)

    dean_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Dekan ismi"
    )
    dean_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Dekan rasmi"
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi?"
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
            FieldPanel('faculty_code'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('short_description_uz'),
            FieldPanel('short_description_ru'),
            FieldPanel('short_description_en'),
        ], heading="Qisqacha tavsif (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
        ], heading="To'liq tavsif (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('dean_name_uz'),
            FieldPanel('dean_name_ru'),
            FieldPanel('dean_name_en'),
            FieldPanel('dean_image'),
        ], heading="Dekan ma'lumotlari"),
        MultiFieldPanel([
            FieldPanel('phone'),
            FieldPanel('email'),
            FieldPanel('office_location_uz'),
            FieldPanel('office_location_ru'),
            FieldPanel('office_location_en'),
        ], heading="Aloqa ma'lumotlari"),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakultetlar"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = 'fakultet'
            slug = base_slug
            counter = 1
            while Faculty.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FacultyAchievement(models.Model):
    """Faculty achievements."""

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    year = models.IntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('faculty'),
        FieldPanel('title_uz'),
        FieldPanel('title_ru'),
        FieldPanel('title_en'),
        FieldPanel('description_uz'),
        FieldPanel('description_ru'),
        FieldPanel('description_en'),
        FieldPanel('year'),
        FieldPanel('link'),
        FieldPanel('image'),
    ]

    class Meta:
        verbose_name = "Yutuq"
        verbose_name_plural = "Yutuqlar"
        ordering = ['-year']

    def __str__(self):
        return self.title


# ============================================
# DEPARTMENTS SECTION
# ============================================

class Department(index.Indexed, models.Model):
    """University department, belongs to a faculty."""

    faculty = models.ForeignKey(
        Faculty,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='departments',
        help_text="Qaysi fakultetga tegishli"
    )

    name = models.CharField(
        max_length=255,
        help_text="Kafedra nomi"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL uchun identifikator (avtomatik yaratiladi)"
    )
    department_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Kafedra kodi"
    )
    short_description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Qisqacha tavsif"
    )
    description = RichTextField(
        blank=True,
        help_text="To'liq tavsif"
    )

    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Muqova rasm"
    )

    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    office_location = models.CharField(max_length=255, blank=True)

    head_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Kafedra mudiri ismi"
    )
    head_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Kafedra mudiri rasmi"
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Tartib raqami"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Faolmi?"
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
            FieldPanel('department_code'),
            FieldPanel('faculty'),
            FieldPanel('cover_image'),
        ], heading="Asosiy ma'lumotlar"),
        MultiFieldPanel([
            FieldPanel('short_description_uz'),
            FieldPanel('short_description_ru'),
            FieldPanel('short_description_en'),
        ], heading="Qisqacha tavsif (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('description_uz'),
            FieldPanel('description_ru'),
            FieldPanel('description_en'),
        ], heading="To'liq tavsif (3 tilda)"),
        MultiFieldPanel([
            FieldPanel('head_name_uz'),
            FieldPanel('head_name_ru'),
            FieldPanel('head_name_en'),
            FieldPanel('head_image'),
        ], heading="Kafedra mudiri"),
        MultiFieldPanel([
            FieldPanel('phone'),
            FieldPanel('email'),
            FieldPanel('office_location_uz'),
            FieldPanel('office_location_ru'),
            FieldPanel('office_location_en'),
        ], heading="Aloqa ma'lumotlari"),
        MultiFieldPanel([
            FieldPanel('order'),
            FieldPanel('is_active'),
        ], heading="Sozlamalar"),
    ]

    class Meta:
        verbose_name = "Kafedra"
        verbose_name_plural = "Kafedralar"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = 'kafedra'
            slug = base_slug
            counter = 1
            while Department.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DepartmentProgram(models.Model):
    """Academic programs offered by department."""

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='programs'
    )
    code = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=255)
    description = RichTextField(blank=True)

    panels = [
        FieldPanel('department'),
        FieldPanel('code'),
        FieldPanel('name_uz'),
        FieldPanel('name_ru'),
        FieldPanel('name_en'),
        FieldPanel('description_uz'),
        FieldPanel('description_ru'),
        FieldPanel('description_en'),
    ]

    class Meta:
        verbose_name = "Dastur"
        verbose_name_plural = "Dasturlar"

    def __str__(self):
        return self.name


class DepartmentSubject(models.Model):
    """Subjects taught at the department."""

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel('department'),
        FieldPanel('name_uz'),
        FieldPanel('name_ru'),
        FieldPanel('name_en'),
        FieldPanel('description_uz'),
        FieldPanel('description_ru'),
        FieldPanel('description_en'),
    ]

    class Meta:
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"

    def __str__(self):
        return self.name


class DepartmentStaff(models.Model):
    """Faculty members and staff at the department."""

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='staff'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('department'),
        FieldPanel('name_uz'),
        FieldPanel('name_ru'),
        FieldPanel('name_en'),
        FieldPanel('email'),
        FieldPanel('image'),
    ]

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"

    def __str__(self):
        return self.name


class DepartmentPublication(models.Model):
    """Research publications from the department."""

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='publications'
    )
    title = models.CharField(max_length=500)
    authors = models.TextField()
    year = models.IntegerField(blank=True, null=True)
    journal_or_conference = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)

    panels = [
        FieldPanel('department'),
        FieldPanel('title_uz'),
        FieldPanel('title_ru'),
        FieldPanel('title_en'),
        FieldPanel('authors'),
        FieldPanel('year'),
        FieldPanel('journal_or_conference'),
        FieldPanel('link'),
    ]

    class Meta:
        verbose_name = "Nashr"
        verbose_name_plural = "Nashrlar"
        ordering = ['-year']

    def __str__(self):
        return self.title