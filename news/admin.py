from django.contrib import admin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel
from .models import TelegramBotConfig, TelegramSyncLog


# Register TelegramBotConfig as a Wagtail Snippet
class TelegramBotConfigViewSet(SnippetViewSet):
    model = TelegramBotConfig
    icon = "site"
    menu_label = "Telegram Bot"
    menu_name = "telegram_bot"
    menu_order = 300
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_display = ['name', 'is_active', 'auto_publish', 'updated_at']
    list_filter = ['is_active', 'auto_publish']
    search_fields = ['name']
    
    panels = [
        FieldPanel('name'),
        FieldPanel('bot_token'),
        FieldPanel('webhook_secret'),
        FieldPanel('channel_id'),
        FieldPanel('is_active'),
        FieldPanel('auto_publish'),
        FieldPanel('news_hashtags'),
        FieldPanel('announcement_hashtags'),
        FieldPanel('admin_user_ids'),
        FieldPanel('default_news_image'),
        FieldPanel('default_announcement_image'),
    ]


class TelegramSyncLogViewSet(SnippetViewSet):
    model = TelegramSyncLog
    icon = "doc-full"
    menu_label = "Telegram Logs"
    menu_name = "telegram_logs"
    menu_order = 301
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_display = ['telegram_message_id', 'status', 'news_page', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['telegram_message_id']


register_snippet(TelegramBotConfigViewSet)
register_snippet(TelegramSyncLogViewSet)


# Also register with Django admin for convenience
@admin.register(TelegramBotConfig)
class TelegramBotConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'auto_publish', 'updated_at']
    list_filter = ['is_active', 'auto_publish']
    search_fields = ['name']
    fieldsets = (
        ('Basic Settings', {
            'fields': ('name', 'bot_token', 'webhook_secret', 'channel_id')
        }),
        ('Behavior', {
            'fields': ('is_active', 'auto_publish')
        }),
        ('Hashtags', {
            'fields': ('news_hashtags', 'announcement_hashtags')
        }),
        ('Admin Users', {
            'fields': ('admin_user_ids',)
        }),
        ('Default Images', {
            'fields': ('default_news_image', 'default_announcement_image'),
            'description': 'Default cover images for posts without photos'
        }),
    )


@admin.register(TelegramSyncLog)
class TelegramSyncLogAdmin(admin.ModelAdmin):
    list_display = ['telegram_message_id', 'telegram_chat_id', 'status', 'news_page', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['telegram_message_id']
    readonly_fields = ['raw_data', 'created_at']
