from modeltranslation.translator import translator, TranslationOptions
from .models import AdmissionYear, AdmissionQuota


class AdmissionYearTranslationOptions(TranslationOptions):
    fields = ('title', 'badge_text', 'hero_title', 'hero_description')


class AdmissionQuotaTranslationOptions(TranslationOptions):
    fields = ('direction_name', 'language')


translator.register(AdmissionYear, AdmissionYearTranslationOptions)
translator.register(AdmissionQuota, AdmissionQuotaTranslationOptions)
