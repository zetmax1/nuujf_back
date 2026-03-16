from modeltranslation.translator import translator, TranslationOptions
from .models import AchievementSection, EnlightenmentSection, Club


class AchievementSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


class EnlightenmentSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'content')


class ClubTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'content')


translator.register(AchievementSection, AchievementSectionTranslationOptions)
translator.register(EnlightenmentSection, EnlightenmentSectionTranslationOptions)
translator.register(Club, ClubTranslationOptions)
