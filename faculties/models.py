from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.blocks import CharBlock, RichTextBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail_localize.models import TranslatableMixin
from wagtail.api import APIField
from rest_framework.fields import Field


# Custom Serializers
class ImageSerializerField(Field):
    """Custom serializer for Wagtail images"""
    def to_representation(self, value):
        if not value:
            return None
        
        try:
            return {
                'id': value.id,
                'title': value.title,
                'url': value.file.url,
                'width': value.width,
                'height': value.height,
            }
        except Exception:
            return None


class DepartmentSerializerField(Field):
    """Serialize departments"""
    def to_representation(self, value):
        return [
            {
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'head_of_department': dept.head_of_department,
            }
            for dept in value.all()
        ]


class AchievementSerializerField(Field):
    """Serialize achievements"""
    def to_representation(self, value):
        return [
            {
                'id': ach.id,
                'title': ach.title,
                'description': ach.description,
                'year': ach.year,
            }
            for ach in value.all()
        ]


# Faculty Index Page
class FacultyIndexPage(Page, TranslatableMixin):
    """Main faculties listing page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    max_count = 1
    subpage_types = ['faculties.FacultyPage']
    
    def get_context(self, request):
        context = super().get_context(request)
        context['faculties'] = FacultyPage.objects.live().public().filter(locale=self.locale)
        return context


# Individual Faculty Page
class FacultyPage(Page, TranslatableMixin):
    """Individual faculty page"""
    faculty_code = models.CharField(max_length=20, blank=True)
    short_description = models.TextField(max_length=500, blank=True)
    description = RichTextField(blank=True)
    
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    office_location = models.CharField(max_length=255, blank=True)
    
    dean_name = models.CharField(max_length=255, blank=True)
    dean_title = models.CharField(max_length=255, blank=True)
    dean_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    dean_bio = RichTextField(blank=True)
    
    content_blocks = StreamField([
        ('heading', CharBlock(classname="title")),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('statistics', StructBlock([
            ('label', CharBlock()),
            ('value', CharBlock()),
        ])),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('faculty_code'),
            FieldPanel('short_description'),
            FieldPanel('cover_image'),
            FieldPanel('logo'),
        ], heading="Basic Information"),
        
        FieldPanel('description'),
        FieldPanel('content_blocks'),
        
        MultiFieldPanel([
            FieldPanel('dean_name'),
            FieldPanel('dean_title'),
            FieldPanel('dean_image'),
            FieldPanel('dean_bio'),
        ], heading="Dean Information"),
        
        MultiFieldPanel([
            FieldPanel('phone'),
            FieldPanel('email'),
            FieldPanel('office_location'),
        ], heading="Contact Information"),
        
        InlinePanel('departments', label="Departments"),
        InlinePanel('achievements', label="Achievements"),
    ]
    
    # API fields
    api_fields = [
        APIField('faculty_code'),
        APIField('short_description'),
        APIField('description'),
        APIField('cover_image', serializer=ImageSerializerField()),
        APIField('logo', serializer=ImageSerializerField()),
        APIField('phone'),
        APIField('email'),
        APIField('office_location'),
        APIField('dean_name'),
        APIField('dean_title'),
        APIField('dean_image', serializer=ImageSerializerField()),
        APIField('dean_bio'),
        APIField('content_blocks'),
        APIField('departments', serializer=DepartmentSerializerField()),
        APIField('achievements', serializer=AchievementSerializerField()),
    ]
    
    parent_page_types = ['faculties.FacultyIndexPage']


# Departments
class FacultyDepartment(ClusterableModel, TranslatableMixin):
    """Departments within a faculty"""
    faculty = ParentalKey(FacultyPage, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    description = RichTextField(blank=True)
    head_of_department = models.CharField(max_length=255, blank=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('head_of_department'),
    ]
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['translation_key', 'locale'],
                name='unique_translation_key_locale_faculties_facultydepartment'
            )
        ]
    
    def __str__(self):
        return self.name


# Achievements
class FacultyAchievement(ClusterableModel, TranslatableMixin):
    """Faculty achievements"""
    faculty = ParentalKey(FacultyPage, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    year = models.IntegerField(blank=True, null=True)
    
    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('year'),
    ]
    
    class Meta:
        ordering = ['-year']
        constraints = [
            models.UniqueConstraint(
                fields=['translation_key', 'locale'],
                name='unique_translation_key_locale_faculties_facultyachievement'
            )
        ]


# ============================================
# DEPARTMENTS SECTION
# ============================================

# Custom Serializer for Department Staff
class DepartmentStaffSerializerField(Field):
    """Serialize department faculty/staff"""
    def to_representation(self, value):
        return [
            {
                'id': staff.id,
                'name': staff.name,
                'title': staff.title,
                'email': staff.email,
                'specialization': staff.specialization,
                'image': {
                    'id': staff.image.id,
                    'title': staff.image.title,
                    'url': staff.image.file.url,
                } if staff.image else None,
            }
            for staff in value.all()
        ]


class DepartmentProgramSerializerField(Field):
    """Serialize department programs"""
    def to_representation(self, value):
        return [
            {
                'id': prog.id,
                'program_type': prog.program_type,
                'code': prog.code,
                'name': prog.name,
                'description': prog.description,
            }
            for prog in value.all()
        ]


class DepartmentSubjectSerializerField(Field):
    """Serialize department subjects"""
    def to_representation(self, value):
        return [
            {
                'id': subj.id,
                'name': subj.name,
                'level': subj.level,
                'credits': subj.credits,
                'description': subj.description,
            }
            for subj in value.all()
        ]


class DepartmentPublicationSerializerField(Field):
    """Serialize department publications"""
    def to_representation(self, value):
        return [
            {
                'id': pub.id,
                'title': pub.title,
                'authors': pub.authors,
                'year': pub.year,
                'journal_or_conference': pub.journal_or_conference,
                'link': pub.link,
            }
            for pub in value.all()
        ]


# Department Index Page
class DepartmentIndexPage(Page, TranslatableMixin):
    """Main departments listing page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    max_count = 1
    subpage_types = ['faculties.DepartmentPage']
    
    def get_context(self, request):
        context = super().get_context(request)
        context['departments'] = DepartmentPage.objects.live().public().filter(locale=self.locale)
        return context


# Individual Department Page
class DepartmentPage(Page, TranslatableMixin):
    """Individual department page"""
    department_code = models.CharField(max_length=20, blank=True)
    short_description = models.TextField(max_length=500, blank=True)
    description = RichTextField(blank=True)
    
    # Faculty reference (optional)
    faculty = models.ForeignKey(
        FacultyPage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='faculty_departments'
    )
    
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    office_location = models.CharField(max_length=255, blank=True)
    
    # Head of Department
    head_name = models.CharField(max_length=255, blank=True)
    head_title = models.CharField(max_length=255, blank=True)
    head_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    head_bio = RichTextField(blank=True)
    
    content_blocks = StreamField([
        ('heading', CharBlock(classname="title")),
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('statistics', StructBlock([
            ('label', CharBlock()),
            ('value', CharBlock()),
        ])),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('department_code'),
            FieldPanel('short_description'),
            FieldPanel('faculty'),
            FieldPanel('cover_image'),
            FieldPanel('logo'),
        ], heading="Basic Information"),
        
        FieldPanel('description'),
        FieldPanel('content_blocks'),
        
        MultiFieldPanel([
            FieldPanel('head_name'),
            FieldPanel('head_title'),
            FieldPanel('head_image'),
            FieldPanel('head_bio'),
        ], heading="Head of Department"),
        
        MultiFieldPanel([
            FieldPanel('phone'),
            FieldPanel('email'),
            FieldPanel('office_location'),
        ], heading="Contact Information"),
        
        InlinePanel('programs', label="Programs"),
        InlinePanel('subjects', label="Subjects"),
        InlinePanel('staff', label="Faculty/Staff"),
        InlinePanel('publications', label="Publications"),
    ]
    
    # API fields
    api_fields = [
        APIField('department_code'),
        APIField('short_description'),
        APIField('description'),
        APIField('faculty'),
        APIField('cover_image', serializer=ImageSerializerField()),
        APIField('logo', serializer=ImageSerializerField()),
        APIField('phone'),
        APIField('email'),
        APIField('office_location'),
        APIField('head_name'),
        APIField('head_title'),
        APIField('head_image', serializer=ImageSerializerField()),
        APIField('head_bio'),
        APIField('content_blocks'),
        APIField('programs', serializer=DepartmentProgramSerializerField()),
        APIField('subjects', serializer=DepartmentSubjectSerializerField()),
        APIField('staff', serializer=DepartmentStaffSerializerField()),
        APIField('publications', serializer=DepartmentPublicationSerializerField()),
    ]
    
    parent_page_types = ['faculties.DepartmentIndexPage']


# Department Programs (Bachelor/Master)
class DepartmentProgram(ClusterableModel, TranslatableMixin):
    """Academic programs offered by department"""
    PROGRAM_TYPES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]
    
    department = ParentalKey(DepartmentPage, on_delete=models.CASCADE, related_name='programs')
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES, default='bachelor')
    code = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=255)
    description = RichTextField(blank=True)
    
    panels = [
        FieldPanel('program_type'),
        FieldPanel('code'),
        FieldPanel('name'),
        FieldPanel('description'),
    ]
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['translation_key', 'locale'],
                name='unique_translation_key_locale_faculties_departmentprogram'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({self.program_type})"


# Department Subjects
class DepartmentSubject(ClusterableModel, TranslatableMixin):
    """Subjects taught at the department"""
    LEVEL_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('both', 'Both'),
    ]
    
    department = ParentalKey(DepartmentPage, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='bachelor')
    credits = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('level'),
        FieldPanel('credits'),
        FieldPanel('description'),
    ]
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['translation_key', 'locale'],
                name='unique_translation_key_locale_faculties_departmentsubject'
            )
        ]
    
    def __str__(self):
        return self.name


# Department Faculty/Staff
class DepartmentStaff(ClusterableModel, TranslatableMixin):
    """Faculty members and staff at the department"""
    department = ParentalKey(DepartmentPage, on_delete=models.CASCADE, related_name='staff')
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    bio = RichTextField(blank=True)
    
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('title'),
        FieldPanel('email'),
        FieldPanel('specialization'),
        FieldPanel('image'),
        FieldPanel('bio'),
    ]
    
    class Meta:
        verbose_name_plural = "Department Staff"
        constraints = [
            models.UniqueConstraint(
                fields=['translation_key', 'locale'],
                name='unique_translation_key_locale_faculties_departmentstaff'
            )
        ]
    
    def __str__(self):
        return self.name


# Department Publications
class DepartmentPublication(ClusterableModel, TranslatableMixin):
    """Research publications from the department"""
    department = ParentalKey(DepartmentPage, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=500)
    authors = models.TextField()
    year = models.IntegerField(blank=True, null=True)
    journal_or_conference = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)
    
    panels = [
        FieldPanel('title'),
        FieldPanel('authors'),
        FieldPanel('year'),
        FieldPanel('journal_or_conference'),
        FieldPanel('link'),
    ]
    
    class Meta:
        ordering = ['-year']
        constraints = [
            models.UniqueConstraint(
                fields=['translation_key', 'locale'],
                name='unique_translation_key_locale_faculties_departmentpublication'
            )
        ]
    
    def __str__(self):
        return self.title