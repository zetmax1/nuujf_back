from modeltranslation.translator import translator, TranslationOptions
from .models import DynamicPage, NavItem, SubNavItem


class DynamicPageTranslationOptions(TranslationOptions):
    fields = ('title', 'body')


class NavItemTranslationOptions(TranslationOptions):
    fields = ('title',)


class SubNavItemTranslationOptions(TranslationOptions):
    fields = ('title',)


translator.register(DynamicPage, DynamicPageTranslationOptions)
translator.register(NavItem, NavItemTranslationOptions)
translator.register(SubNavItem, SubNavItemTranslationOptions)
