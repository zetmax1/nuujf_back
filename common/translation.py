from modeltranslation.translator import translator, TranslationOptions
from .models import Vacancy


class VacancyTranslationOptions(TranslationOptions):
    fields = ('title', 'department', 'description', 'requirements')


translator.register(Vacancy, VacancyTranslationOptions)
