from modeltranslation.translator import register, TranslationOptions
from .models import ScienceIndex, ResearchArea, ResearchDetail

@register(ScienceIndex)
class ScienceIndexTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 
              'stat1_label', 'stat2_label', 'stat3_label', 'stat4_label')

@register(ResearchArea)
class ResearchAreaTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(ResearchDetail)
class ResearchDetailTranslationOptions(TranslationOptions):
    fields = ('subtitle', 'content', 
              'stat1_label', 'stat2_label', 'stat3_label')
