from modeltranslation.translator import translator, TranslationOptions
from .models import Leader, StructureSection, SectionMember


class LeaderTranslationOptions(TranslationOptions):
    fields = ('full_name', 'position', 'academic_degree', 'reception_days', 'bio')


class StructureSectionTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class SectionMemberTranslationOptions(TranslationOptions):
    fields = ('full_name', 'position')


translator.register(Leader, LeaderTranslationOptions)
translator.register(StructureSection, StructureSectionTranslationOptions)
translator.register(SectionMember, SectionMemberTranslationOptions)
