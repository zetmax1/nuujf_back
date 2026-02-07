from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page
from .models import NewsPage, NewsImage, TelegramBotConfig, TelegramSyncLog


class NewsPageModelTest(TestCase):
    """Tests for NewsPage model"""
    
    def setUp(self):
        # Get root page
        self.root_page = Page.objects.get(depth=1)
    
    def test_news_page_str(self):
        """Test string representation"""
        # Note: We can't easily create NewsPage without NewsIndexPage as parent
        # This is a basic model test
        config = TelegramBotConfig.objects.create(
            name="Test Bot",
            bot_token="test_token"
        )
        self.assertEqual(str(config), "Test Bot")


class TelegramBotConfigTest(TestCase):
    """Tests for TelegramBotConfig model"""
    
    def test_get_news_hashtags(self):
        """Test hashtag parsing"""
        config = TelegramBotConfig.objects.create(
            name="Test Bot",
            news_hashtags="#yangilik, #news, #НОВОСТЬ"
        )
        hashtags = config.get_news_hashtags()
        self.assertIn('#yangilik', hashtags)
        self.assertIn('#news', hashtags)
        self.assertIn('#новость', hashtags)  # Should be lowercased
    
    def test_get_announcement_hashtags(self):
        """Test announcement hashtag parsing"""
        config = TelegramBotConfig.objects.create(
            name="Test Bot",
            announcement_hashtags="#elon, #announcement"
        )
        hashtags = config.get_announcement_hashtags()
        self.assertEqual(len(hashtags), 2)
        self.assertIn('#elon', hashtags)


class TelegramSyncLogTest(TestCase):
    """Tests for TelegramSyncLog model"""
    
    def test_sync_log_creation(self):
        """Test creating sync log"""
        log = TelegramSyncLog.objects.create(
            telegram_message_id=12345,
            telegram_chat_id=-100123456789,
            status='success',
            raw_data={'test': 'data'}
        )
        self.assertEqual(log.status, 'success')
        self.assertEqual(str(log), "Sync 12345 - success")
    
    def test_duplicate_prevention(self):
        """Test unique constraint"""
        TelegramSyncLog.objects.create(
            telegram_message_id=12345,
            telegram_chat_id=-100123456789,
            status='success'
        )
        # Second creation with same IDs should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TelegramSyncLog.objects.create(
                telegram_message_id=12345,
                telegram_chat_id=-100123456789,
                status='duplicate'
            )
