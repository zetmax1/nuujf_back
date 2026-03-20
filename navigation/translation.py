from modeltranslation.translator import translator, TranslationOptions
from .models import DynamicPage, NavItem, SubNavItem, TopBarLink


class DynamicPageTranslationOptions(TranslationOptions):
    fields = ('title', 'body')


class NavItemTranslationOptions(TranslationOptions):
    fields = ('title',)


class SubNavItemTranslationOptions(TranslationOptions):
    fields = ('title',)


class TopBarLinkTranslationOptions(TranslationOptions):
    fields = ('title',)


translator.register(DynamicPage, DynamicPageTranslationOptions)
translator.register(NavItem, NavItemTranslationOptions)
translator.register(SubNavItem, SubNavItemTranslationOptions)
translator.register(TopBarLink, TopBarLinkTranslationOptions)
