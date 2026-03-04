from modeltranslation.translator import translator, TranslationOptions
from .models import ActivityCategory, ActivityPage


class ActivityCategoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class ActivityPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


translator.register(ActivityCategory, ActivityCategoryTranslationOptions)
translator.register(ActivityPage, ActivityPageTranslationOptions)
