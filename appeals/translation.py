from modeltranslation.translator import translator, TranslationOptions
from .models import Appeal


class AppealTranslationOptions(TranslationOptions):
    fields = ('department', 'message')


translator.register(Appeal, AppealTranslationOptions)
