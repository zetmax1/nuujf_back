from modeltranslation.translator import translator, TranslationOptions
from .models import CollaborationType, PartnerOrganization, CollaborationProject, CollaborationPage


class CollaborationTypeTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class PartnerOrganizationTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'country')


class CollaborationProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


class CollaborationPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


translator.register(CollaborationType, CollaborationTypeTranslationOptions)
translator.register(PartnerOrganization, PartnerOrganizationTranslationOptions)
translator.register(CollaborationProject, CollaborationProjectTranslationOptions)
translator.register(CollaborationPage, CollaborationPageTranslationOptions)
