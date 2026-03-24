from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache

class CachedViewMixin:
    """
    Mixin to cache Django and DRF class-based views.
    By default caches for 10 minutes (60 * 10 seconds).
    """
    cache_timeout = 60 * 10

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        return cache_page(cls.cache_timeout)(view)

class NoCacheMixin:
    """
    Mixin to explicitly prevent caching of a view.
    """
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
