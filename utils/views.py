from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


@method_decorator(staff_member_required, name='dispatch')
class ClearCacheView(View):
    """A view that clears all Django caches and redirects back to Wagtail admin."""

    def get(self, request):
        cache.clear()
        messages.success(request, "✅ Cache cleared successfully!")
        return redirect('wagtailadmin_home')

    def post(self, request):
        cache.clear()
        messages.success(request, "✅ Cache cleared successfully!")
        return redirect('wagtailadmin_home')
