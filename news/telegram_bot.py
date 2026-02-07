"""
Telegram Bot for University News & Announcements
Handles commands, menus, and interactive features
"""
import logging
import os
import tempfile
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from django.utils import timezone
from django.core.files import File
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


# Helper functions wrapped for async
@sync_to_async
def get_latest_news():
    """Get latest 5 news"""
    from .models import NewsPage
    return list(NewsPage.objects.live().public()
                .filter(post_type='news')
                .order_by('-published_date')[:5])


@sync_to_async
def get_latest_announcements():
    """Get latest 5 announcements"""
    from .models import NewsPage
    return list(NewsPage.objects.live().public()
                .filter(post_type='announcement')
                .order_by('-published_date')[:5])


@sync_to_async
def get_todays_news(today_start, today_end):
    """Get today's news"""
    from .models import NewsPage
    return list(NewsPage.objects.live().public()
                .filter(
                    post_type='news',
                    published_date__gte=today_start,
                    published_date__lt=today_end
                )
                .order_by('-published_date'))


@sync_to_async
def get_recent_posts():
    """Get recent posts"""
    from .models import NewsPage
    return list(NewsPage.objects.live().public()
                .order_by('-published_date')[:10])


class UniversityNewsBot:
    """Main bot class for handling Telegram interactions"""
    
    def __init__(self, token):
        self.token = token
        self.application = None
        
        # Admin user IDs (can be configured dynamically later)
        self.admin_ids = set()
    
    def setup(self):
        """Setup bot handlers"""
        self.application = Application.builder().token(self.token).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("news", self.news_command))
        self.application.add_handler(CommandHandler("announcements", self.announcements_command))
        self.application.add_handler(CommandHandler("post", self.post_command))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Photo handler FIRST (before text handler)
        self.application.add_handler(
            MessageHandler(filters.PHOTO, self.handle_photo)
        )
        
        # Message handler for posting news
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        logger.info("Bot handlers registered successfully")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [KeyboardButton("📰 Today's News"), KeyboardButton("📢 Announcements")],
            [KeyboardButton("📋 Recent Posts"), KeyboardButton("ℹ️ Help")],
        ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        welcome_text = (
            "🎓 *Welcome to University News Bot!*\n\n"
            "Stay updated with the latest news and announcements from our university.\n\n"
            "*Quick Menu:*\n"
            "📰 Today's News - View today's news\n"
            "📢 Announcements - View recent announcements\n"
            "📋 Recent Posts - View all recent posts\n"
            "\n*Commands:*\n"
            "/news - View latest news\n"
            "/announcements - View latest announcements\n"
            "/help - Show this help message\n\n"
            "📝 *Admins can post:*\n"
            "Send text or photo with caption + #yangilik or #elon"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🎓 *University News Bot - Help*\n\n"
            "*Available Commands:*\n"
            "/start - Show main menu\n"
            "/news - View latest news (yangiliklar)\n"
            "/announcements - View latest announcements (e'lonlar)\n"
            "/help - Show this help message\n\n"
            "*Quick Buttons:*\n"
            "📰 Today's News - News from today\n"
            "📢 Announcements - Recent announcements\n"
            "📋 Recent Posts - All recent posts\n\n"
            "*Admin Posting:*\n"
            "Send message with #yangilik or #elon hashtag\n"
            "Can include photos!\n\n"
            "💡 *Tip:* Use the menu buttons for quick access!"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command - show latest news"""
        news_items = await get_latest_news()
        
        if not news_items:
            await update.message.reply_text("📭 No news available at the moment.")
            return
        
        response = "📰 *Latest News:*\n\n"
        for idx, item in enumerate(news_items, 1):
            pub_date = item.published_date.strftime('%d.%m.%Y')
            response += f"{idx}. *{item.title}*\n"
            if item.excerpt:
                response += f"   _{item.excerpt[:100]}..._\n"
            response += f"   📅 {pub_date}\n\n"
        
        # Add inline buttons for more details
        keyboard = [[InlineKeyboardButton("🌐 View on Website", url="http://your-domain.com/news")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def announcements_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /announcements command"""
        announcements = await get_latest_announcements()
        
        if not announcements:
            await update.message.reply_text("📭 No announcements available.")
            return
        
        response = "📢 *Latest Announcements:*\n\n"
        for idx, item in enumerate(announcements, 1):
            pub_date = item.published_date.strftime('%d.%m.%Y')
            response += f"{idx}. *{item.title}*\n"
            if item.excerpt:
                response += f"   _{item.excerpt[:100]}..._\n"
            response += f"   📅 {pub_date}\n\n"
        
        keyboard = [[InlineKeyboardButton("🌐 View on Website", url="http://your-domain.com/news")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def post_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /post command - admin only"""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if not await self.is_admin(user_id):
            await update.message.reply_text(
                "⛔ This command is only available for administrators."
            )
            return
        
        instructions = (
            "📝 *Post News/Announcement*\n\n"
            "*Text Format:*\n"
            "```\n"
            "Title\n"            "Content goes here.\n"
            "#yangilik (news) or #elon (announcement)\n"
            "```\n\n"
            "*Photo Format:*\n"
            "Send photo with caption:\n"
            "```\n"
            "Title\n"
            "Description\n"
            "#yangilik\n"
            "```\n\n"
            "💡 Photos are automatically attached!"
        )
        
        await update.message.reply_text(instructions, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages - either menu buttons or posts"""
        text = update.message.text
        
        # Handle menu button presses
        if text == "📰 Today's News":
            await self.show_todays_news(update, context)
        elif text == "📢 Announcements":
            await self.announcements_command(update, context)
        elif text == "📋 Recent Posts":
            await self.show_recent_posts(update, context)
        elif text == "ℹ️ Help":
            await self.help_command(update, context)
        else:
            # Check if it's a news post from admin
            user_id = update.effective_user.id
            if await self.is_admin(user_id) and ('#yangilik' in text.lower() or '#elon' in text.lower() or '#news' in text.lower()):
                await self.create_news_from_message(update, context)
            else:
                await update.message.reply_text(
                    "Use the menu buttons or /help to see available commands."
                )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages"""
        user_id = update.effective_user.id
        
        if not await self.is_admin(user_id):
            await update.message.reply_text("⛔ Only admins can post news.")
            return
        
        caption = update.message.caption or ""
        
        if '#yangilik' in caption.lower() or '#elon' in caption.lower() or '#news' in caption.lower():
            # This is a news post with image
            await self.create_news_from_photo(update, context)
        else:
            await update.message.reply_text(
                "Add #yangilik or #elon hashtag to post this as news."
            )
    
    async def show_todays_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show today's news"""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        news_items = await get_todays_news(today_start, today_end)
        
        if not news_items:
            await update.message.reply_text("📭 No news posted today yet.")
            return
        
        response = f"📰 *Today's News ({len(news_items)})*\n\n"
        for idx, item in enumerate(news_items, 1):
            time_str = item.published_date.strftime('%H:%M')
            response += f"{idx}. *{item.title}*\n"
            if item.excerpt:
                response += f"   _{item.excerpt[:100]}..._\n"
            response += f"   🕐 {time_str}\n\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def show_recent_posts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent posts (all types)"""
        recent_items = await get_recent_posts()
        
        if not recent_items:
            await update.message.reply_text("📭 No posts available.")
            return
        
        response = "📋 *Recent Posts:*\n\n"
        for idx, item in enumerate(recent_items, 1):
            icon = "📰" if item.post_type == 'news' else "📢"
            pub_date = item.published_date.strftime('%d.%m %H:%M')
            response += f"{icon} *{item.title}*\n"
            response += f"   📅 {pub_date}\n\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    async def create_news_from_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, photo_file=None):
        """Create NewsPage from admin message"""
        from .models import NewsPage, TelegramBotConfig, TelegramSyncLog
        from wagtail.models import Page
        from wagtail.images.models import Image
        from django.utils.text import slugify
        import re
        
        text = update.message.caption if photo_file else update.message.text
        message_id = update.message.message_id
        chat_id = update.message.chat_id
        
        # Get bot config
        @sync_to_async
        def get_bot_config():
            return TelegramBotConfig.objects.filter(is_active=True).first()
        
        config = await get_bot_config()
        if not config:
            await update.message.reply_text("⚠️ Bot not configured properly.")
            return
        
        # Determine post type
        text_lower = text.lower()
        post_type = 'announcement' if any(h in text_lower for h in config.get_announcement_hashtags()) else 'news'
        
        # Extract title and content
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else 'Telegram Post'
        title = re.sub(r'#\w+', '', title).strip()
        
        excerpt = re.sub(r'#\w+', '', text[:200]).strip()
        
        try:
            # Find parent page
            @sync_to_async
            def get_parent_page():
                return Page.objects.filter(content_type__model='newsindexpage').first()
            
            parent_page = await get_parent_page()
            
            if not parent_page:
                await update.message.reply_text("⚠️ NewsIndexPage not found. Create it in admin first.")
                return
            
            # Generate unique slug
            base_slug = slugify(title[:50]) or f'telegram-{message_id}'
            slug = base_slug
            counter = 1
            
            @sync_to_async
            def slug_exists(s):
                return NewsPage.objects.filter(slug=s).exists()
            
            while await slug_exists(slug):
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Handle image (either from photo or use default)
            cover_image_id = None
            if photo_file:
                cover_image_id = await sync_to_async(self._save_telegram_image)(photo_file, title)
            elif config.default_news_image_id and post_type == 'news':
                cover_image_id = config.default_news_image_id
            elif config.default_announcement_image_id and post_type == 'announcement':
                cover_image_id = config.default_announcement_image_id
            
            # Create news page
            @sync_to_async
            def create_and_publish():
                news_page = NewsPage(
                    title=title,
                    slug=slug,
                    post_type=post_type,
                    excerpt=excerpt,
                    content=text,
                    published_date=timezone.now(),
                    telegram_message_id=message_id,
                    telegram_chat_id=chat_id,
                    synced_from_telegram=True,
                )
                
                # Set cover image if available
                if cover_image_id:
                    news_page.cover_image_id = cover_image_id
                
                # Add as child and publish
                parent_page.add_child(instance=news_page)
                if config.auto_publish:
                    revision = news_page.save_revision()
                    revision.publish()
                
                # Create log
                TelegramSyncLog.objects.create(
                    telegram_message_id=message_id,
                    telegram_chat_id=chat_id,
                    news_page=news_page,
                    status='success',
                    raw_data={'text': text, 'has_photo': photo_file is not None}
                )
                
                return news_page, config.auto_publish
            
            news_page, auto_publish = await create_and_publish()
            
            type_emoji = "📰" if post_type == 'news' else "📢"
            status = "published" if auto_publish else "saved as draft"
            photo_status = " 📸 with photo" if photo_file else ""
            
            await update.message.reply_text(
                f"✅ {type_emoji} *{post_type.capitalize()} {status}!*{photo_status}\n\n"
                f"Title: {title}\n"
                f"ID: {news_page.id}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error creating news: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def create_news_from_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create news from photo message"""
        # Get the highest quality photo
        photo = update.message.photo[-1]
        
        # Download the photo
        photo_file = await photo.get_file()
        
        # Create news with photo
        await self.create_news_from_message(update, context, photo_file=photo_file)
    
    def _save_telegram_image(self, photo_file, title):
        """Save Telegram photo to Wagtail Image (sync function)"""
        from wagtail.images.models import Image
        import requests
        
        try:
            # Download photo
            response = requests.get(photo_file.file_path)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Create Wagtail Image
            with open(temp_path, 'rb') as f:
                wagtail_image = Image(
                    title=f"Telegram: {title}"[:255],
                    file=File(f, name=f"telegram_{photo_file.file_id[:20]}.jpg")
                )
                wagtail_image.save()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return wagtail_image.id
            
        except Exception as e:
            logger.error(f"Error saving Telegram image: {e}", exc_info=True)
            return None
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        # Handle different callback data
        # Can be extended for more interactive features
        
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        @sync_to_async
        def check_admin():
            from .models import TelegramBotConfig
            config = TelegramBotConfig.objects.filter(is_active=True).first()
            if not config:
                return False
            return config.is_admin(user_id)
        
        return await check_admin()
    
    def run_polling(self):
        """Run bot with polling (for development)"""
        if not self.application:
            self.setup()
        
        logger.info("Starting bot with polling...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def set_webhook(self, webhook_url: str):
        """Set webhook for production"""
        if not self.application:
            self.setup()
        
        await self.application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
