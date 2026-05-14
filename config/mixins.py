from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.vary import vary_on_headers


class CachedViewMixin:
    """
    Mixin to cache Django and DRF class-based views (ViewSets + generic views).

    By default caches for 10 minutes (60 * 10 seconds).

    Patches dispatch() so ALL routes are cached — including DRF ViewSet
    @action methods like latest_for_home, pinned, announcements, etc.
    The original as_view() approach missed these @action routes entirely.

    Varies the cache key on Accept-Language so multilingual responses
    are cached separately per locale.
    """
    cache_timeout = 60 * 10

    @method_decorator(vary_on_headers('Accept-Language'))
    def dispatch(self, request, *args, **kwargs):
        # Wrap the entire dispatch in cache_page so every action is cached
        return cache_page(self.cache_timeout)(
            super().dispatch
        )(request, *args, **kwargs)


class NoCacheMixin:
    """
    Mixin to explicitly prevent caching of a view.
    """
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
