from modeltranslation.translator import translator, TranslationOptions
from .models import (
    Faculty, FacultyAchievement,
    Department, DepartmentProgram, DepartmentSubject,
    DepartmentStaff, DepartmentPublication,
)


class FacultyTranslationOptions(TranslationOptions):
    fields = ('name', 'short_description', 'description', 'dean_name', 'office_location')


class FacultyAchievementTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name', 'short_description', 'description', 'head_name', 'office_location', 'reception_time')


class DepartmentProgramTranslationOptions(TranslationOptions):
    fields = ('name',)


class DepartmentSubjectTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class DepartmentStaffTranslationOptions(TranslationOptions):
    fields = ('name',)


class DepartmentPublicationTranslationOptions(TranslationOptions):
    fields = ('title',)


translator.register(Faculty, FacultyTranslationOptions)
translator.register(FacultyAchievement, FacultyAchievementTranslationOptions)
translator.register(Department, DepartmentTranslationOptions)
translator.register(DepartmentProgram, DepartmentProgramTranslationOptions)
translator.register(DepartmentSubject, DepartmentSubjectTranslationOptions)
translator.register(DepartmentStaff, DepartmentStaffTranslationOptions)
translator.register(DepartmentPublication, DepartmentPublicationTranslationOptions)
