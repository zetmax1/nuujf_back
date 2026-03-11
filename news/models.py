from django.db import models
from django.utils import timezone
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.images import get_image_model
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail_localize.models import TranslatableMixin
from rest_framework.fields import Field


# ============================================
# CUSTOM SERIALIZERS FOR API
# ============================================

class ImageSerializerField(Field):
    """Custom serializer for Wagtail images"""
    def to_representation(self, value):
        if not value:
            return None
        return {
            'id': value.id,
            'title': value.title,
            'url': value.file.url,
            'width': value.width,
            'height': value.height,
        }


class NewsImageSerializerField(Field):
    """Serialize news images gallery"""
    def to_representation(self, value):
        return [
            {
                'id': img.id,
                'caption': img.caption,
                'image': {
                    'id': img.image.id,
                    'title': img.image.title,
                    'url': img.image.file.url,
                    'width': img.image.width,
                    'height': img.image.height,
                } if img.image else None
            }
            for img in value.all()
        ]


# ============================================
# NEWS & ANNOUNCEMENTS MODELS
# ============================================

class NewsIndexPage(Page):
    """Main news/announcements listing page"""
    intro = RichTextField(blank=True, help_text="Introduction text for the news page")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    max_count = 1
    subpage_types = ['news.NewsPage']
    
    def get_context(self, request):
        context = super().get_context(request)
        # Get all published news, ordered by date
        context['news_items'] = NewsPage.objects.live().public().order_by('-published_date')
        return context
    
    class Meta:
        verbose_name = "News Index Page"


class NewsPage(Page):
    """Individual news or announcement page"""
    
    POST_TYPE_CHOICES = [
        ('news', 'Yangilik (News)'),
        ('announcement', "E'lon (Announcement)"),
    ]
    
    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        default='news',
        help_text="Type of post: news or announcement"
    )
    
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short summary for listing pages"
    )
    
    content = RichTextField(
        blank=True,
        help_text="Full content of the news/announcement"
    )
    
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Main cover image"
    )
    
    published_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date when this was published"
    )
    
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin this item to top of listings"
    )
    
    views_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of views"
    )
    
    # Telegram integration fields
    telegram_message_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Telegram message ID if synced from Telegram"
    )
    
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Telegram chat/channel ID"
    )
    
    synced_from_telegram = models.BooleanField(
        default=False,
        help_text="Whether this was created from Telegram"
    )
    
    # Panels for Wagtail admin
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('post_type'),
            FieldPanel('is_pinned'),
            FieldPanel('published_date'),
        ], heading="Post Settings"),
        FieldPanel('excerpt'),
        FieldPanel('cover_image'),
        FieldPanel('content'),
        InlinePanel('gallery_images', label="Gallery Images"),
    ]
    
    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('telegram_message_id', read_only=True),
            FieldPanel('telegram_chat_id', read_only=True),
            FieldPanel('synced_from_telegram', read_only=True),
        ], heading="Telegram Sync Info"),
    ]
    
    # API fields
    api_fields = [
        APIField('post_type'),
        APIField('excerpt'),
        APIField('content'),
        APIField('cover_image', serializer=ImageSerializerField()),
        APIField('published_date'),
        APIField('is_pinned'),
        APIField('views_count'),
        APIField('gallery_images', serializer=NewsImageSerializerField()),
    ]
    
    parent_page_types = ['news.NewsIndexPage']
    
    class Meta:
        verbose_name = "News/Announcement"
        verbose_name_plural = "News/Announcements"
        ordering = ['-is_pinned', '-published_date']
    
    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.title}"


class NewsImage(models.Model):
    """Gallery images for a news/announcement"""
    
    news = ParentalKey(
        NewsPage,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    caption = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional caption for the image"
    )
    
    sort_order = models.PositiveIntegerField(default=0)
    
    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
    
    class Meta:
        ordering = ['sort_order']
        verbose_name = "News Image"
        verbose_name_plural = "News Images"
    
    def __str__(self):
        return f"Image for {self.news.title}"


# ============================================
# TELEGRAM BOT CONFIGURATION
# ============================================

class TelegramBotConfig(models.Model):
    """Configuration for Telegram bot integration"""
    
    name = models.CharField(
        max_length=100,
        default="University News Bot",
        help_text="Bot display name"
    )
    
    bot_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Telegram Bot API token from @BotFather"
    )
    
    webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secret for webhook verification"
    )
    
    channel_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Telegram channel ID to sync from"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable bot integration"
    )
    
    auto_publish = models.BooleanField(
        default=True,
        help_text="Automatically publish synced posts (or save as draft)"
    )
    
    news_hashtags = models.CharField(
        max_length=255,
        default="#yangilik,#news,#новость",
        help_text="Comma-separated hashtags that indicate news"
    )
    
    announcement_hashtags = models.CharField(
        max_length=255,
        default="#elon,#announcement,#объявление",
        help_text="Comma-separated hashtags that indicate announcements"
    )
    
    admin_user_ids = models.TextField(
        blank=True,
        help_text="Comma-separated Telegram user IDs of admins who can post news (leave empty to allow all)"
    )
    
    website_url = models.URLField(
        max_length=255,
        default="https://example.com",
        help_text="Base URL of the website (for 'View on Website' button in bot)"
    )
    
    default_news_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Default cover image for news without photos"
    )
    
    default_announcement_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Default cover image for announcements without photos"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Telegram Bot Config"
        verbose_name_plural = "Telegram Bot Configs"
    
    def __str__(self):
        return self.name
    
    def get_news_hashtags(self):
        """Return list of news hashtags"""
        return [h.strip().lower() for h in self.news_hashtags.split(',') if h.strip()]
    
    def get_announcement_hashtags(self):
        """Return list of announcement hashtags"""
        return [h.strip().lower() for h in self.announcement_hashtags.split(',') if h.strip()]
    
    def get_admin_user_ids(self):
        """Return set of admin user IDs"""
        if not self.admin_user_ids:
            return set()
        return {int(uid.strip()) for uid in self.admin_user_ids.split(',') if uid.strip().isdigit()}
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user ID is admin"""
        admin_ids = self.get_admin_user_ids()
        # If no admins configured, allow all (for initial setup)
        if not admin_ids:
            return True
        return user_id in admin_ids


class TelegramSyncLog(models.Model):
    """Log of synced Telegram messages"""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('duplicate', 'Duplicate'),
    ]
    
    telegram_message_id = models.BigIntegerField()
    telegram_chat_id = models.BigIntegerField()
    
    news_page = models.ForeignKey(
        NewsPage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='telegram_logs'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success'
    )
    
    error_message = models.TextField(blank=True)
    
    raw_data = models.JSONField(
        default=dict,
        help_text="Raw Telegram message data"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Telegram Sync Log"
        verbose_name_plural = "Telegram Sync Logs"
        unique_together = ['telegram_message_id', 'telegram_chat_id']
    
    def __str__(self):
        return f"Sync {self.telegram_message_id} - {self.status}"
