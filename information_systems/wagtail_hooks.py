from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import InformationSystem

class InformationSystemViewSet(SnippetViewSet):
    model = InformationSystem
    menu_label = "Axborot tizimlari"
    icon = "site"
    add_to_admin_menu = True
    list_display = ["name", "link", "order"]
    search_fields = ["name", "short_description"]


register_snippet(InformationSystemViewSet)
