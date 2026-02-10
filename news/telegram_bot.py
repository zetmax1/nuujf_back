"""
Telegram Bot for University News & Announcements
Handles commands, menus, interactive features, and media groups
"""
import logging
import os
import tempfile
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
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
        
        # Store media groups temporarily (media_group_id -> list of photos)
        self.media_groups = defaultdict(list)
        self.media_group_tasks = {}  # media_group_id -> asyncio.Task
    
    def setup(self):
        """Setup bot handlers"""
        self.application = Application.builder().token(self.token).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("news", self.news_command))
        self.application.add_handler(CommandHandler("announcements", self.announcements_command))
        self.application.add_handler(CommandHandler("post", self.post_command))
        self.application.add_handler(CommandHandler("myid", self.my_id_command))
        
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
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Bot handlers registered successfully")
    
    async def error_handler(self, update, context):
        """Handle errors globally"""
        import telegram.error
        
        # Ignore network timeout errors (they auto-recover)
        if isinstance(context.error, (telegram.error.TimedOut, telegram.error.NetworkError)):
            logger.warning(f"Network error (auto-recoverable): {context.error}")
            return
        
        logger.error(f"Bot error: {context.error}", exc_info=context.error)
        
        # Try to notify user
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    f"❌ *An error occurred:*\n`{str(context.error)[:200]}`",
                    parse_mode='Markdown'
                )
            except Exception:
                pass  # Can't send the error message, ignore
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "User"
        logger.info(f"User started bot - ID: {user_id}, Username: @{username}")
        
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
            "/myid - Get your Telegram user ID\n"
            "/help - Show this help message\n\n"
            "📝 *Admins can post:*\n"
            "Send text or photo(s) with caption + #yangilik or #elon"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def my_id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user their Telegram ID"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "N/A"
        first_name = update.effective_user.first_name or ""
        
        await update.message.reply_text(
            f"👤 *Your Telegram Info:*\n\n"
            f"🆔 User ID: `{user_id}`\n"
            f"👤 Username: @{username}\n"
            f"📝 Name: {first_name}\n\n"
            f"💡 Copy your User ID to give to the admin for posting permissions.",
            parse_mode='Markdown'
        )
        logger.info(f"User ID request - ID: {user_id}, Username: @{username}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🎓 *University News Bot - Help*\n\n"
            "*Available Commands:*\n"
            "/start - Show main menu\n"
            "/news - View latest news (yangiliklar)\n"
            "/announcements - View latest announcements (e'lonlar)\n"
            "/myid - Get your Telegram user ID\n"
            "/help - Show this help message\n\n"
            "*Quick Buttons:*\n"
            "📰 Today's News - News from today\n"
            "📢 Announcements - Recent announcements\n"
            "📋 Recent Posts - All recent posts\n\n"
            "*Admin Posting:*\n"
            "Send message with #yangilik or #elon hashtag\n"
            "Can include single photo or album (multiple photos)!\n\n"
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
                "⛔ This command is only available for administrators.\n\n"
                f"Your User ID: `{user_id}`\n"
                "Ask admin to add your ID to authorized users.",
                parse_mode='Markdown'
            )
            return
        
        instructions = (
            "📝 *Post News/Announcement*\n\n"
            "*Text Format:*\n"
            "```\n"
            "Title\n"
            "Content goes here.\n"
            "#yangilik (news) or #elon (announcement)\n"
            "```\n\n"
            "*Single Photo:*\n"
            "Send photo with caption (title + #hashtag)\n\n"
            "*Multiple Photos (Album):*\n"
            "Select 2-10 photos, add caption to first photo:\n"
            "```\n"
            "Title\n"
            "Description\n"
            "#yangilik\n"
            "```\n"
            "All photos will be added as gallery!\n\n"
            "💡 Bot will wait 3 seconds to collect all photos from album."
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
        """Handle photo messages - supports single photos and albums"""
        user_id = update.effective_user.id
        
        # Check admin first
        if not await self.is_admin(user_id):
            await update.message.reply_text(
                "⛔ *Sorry, only administrators can post news.*\n\n"
                f"Your Telegram ID: `{user_id}`\n"
                "Ask an admin to add your ID to the authorized users list.",
                parse_mode='Markdown'
            )
            return
        
        caption = update.message.caption or ""
        media_group_id = update.message.media_group_id
        
        # ALBUMS: collect photos first, validate later
        # In an album only the first photo has caption, rest are empty
        if media_group_id:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            
            self.media_groups[media_group_id].append({
                'file': photo_file,
                'caption': caption,
                'message': update.message
            })
            
            # Cancel previous timer if exists
            if media_group_id in self.media_group_tasks:
                self.media_group_tasks[media_group_id].cancel()
            
            # Wait 3 seconds for all album photos to arrive, then process
            async def process_media_group():
                await asyncio.sleep(3)
                await self.create_news_from_media_group(media_group_id, update, context)
            
            task = asyncio.create_task(process_media_group())
            self.media_group_tasks[media_group_id] = task
            return
        
        # SINGLE PHOTO: validate caption and hashtag
        if not caption.strip():
            await update.message.reply_text(
                "⚠️ *Photo needs a caption!*\n\n"
                "Please add a caption with:\n"
                "• Title (first line)\n"
                "• Description\n"
                "• Hashtag: #yangilik (news) or #elon (announcement)\n\n"
                "*Example:*\n"
                "```\n"
                "Library Opens Tomorrow\n"
                "New facilities available!\n"
                "#yangilik\n"
                "```",
                parse_mode='Markdown'
            )
            return
        
        has_hashtag = '#yangilik' in caption.lower() or '#elon' in caption.lower() or '#news' in caption.lower()
        
        if not has_hashtag:
            await update.message.reply_text(
                "⚠️ *Missing hashtag!*\n\n"
                "Add one of these hashtags to your caption:\n"
                "• #yangilik - for news (yangiliklar)\n"
                "• #elon - for announcements (e'lonlar)\n\n"
                "*Your caption:*\n"
                f"```\n{caption}\n```\n"
                "_(Add hashtag and resend)_",
                parse_mode='Markdown'
            )
            return
        
        # Single photo with valid caption and hashtag
        await self.create_news_from_photo(update, context)
    
    async def create_news_from_media_group(self, media_group_id, update, context):
        """Create news from a media group (album of photos)"""
        photos = self.media_groups.get(media_group_id, [])
        logger.info(f"Processing media group {media_group_id} with {len(photos)} photos")
        
        if not photos:
            logger.warning(f"No photos found for media group {media_group_id}")
            return
        
        # Find the photo with caption (usually the first one)
        caption_photo = next((p for p in photos if p['caption']), photos[0])
        caption = caption_photo['caption']
        
        # Validate caption exists
        if not caption or not caption.strip():
            await caption_photo['message'].reply_text(
                f"⚠️ *Album needs a caption!*\n\n"
                f"You sent {len(photos)} photos but no caption.\n\n"
                "Add caption to first photo with:\n"
                "• Title and description\n"
                "• #yangilik or #elon\n\n"
                "*Then resend the album.*",
                parse_mode='Markdown'
            )
            del self.media_groups[media_group_id]
            return
        
        # Check for hashtag
        if not ('#yangilik' in caption.lower() or '#elon' in caption.lower() or '#news' in caption.lower()):
            await caption_photo['message'].reply_text(
                f"⚠️ *Missing hashtag!*\n\n"
                f"Album has {len(photos)} photos but caption missing hashtag.\n\n"
                "*Your caption:*\n"
                f"```\n{caption}\n```\n\n"
                "Add #yangilik or #elon and resend album.",
                parse_mode='Markdown'
            )
            del self.media_groups[media_group_id]
            return
        
        try:
            # Create a fake update-like object so create_news_from_message works
            from types import SimpleNamespace
            fake_update = SimpleNamespace(message=caption_photo['message'])
            
            photo_files = [p['file'] for p in photos]
            logger.info(f"Creating news from album: {len(photo_files)} photos, caption: {caption[:50]}")
            
            await self.create_news_from_message(
                fake_update,
                context,
                photo_files=photo_files
            )
        except Exception as e:
            logger.error(f"Error creating news from media group: {e}", exc_info=True)
            await caption_photo['message'].reply_text(
                f"❌ *Error creating news from album:*\n`{str(e)}`",
                parse_mode='Markdown'
            )
        finally:
            # Clean up
            if media_group_id in self.media_groups:
                del self.media_groups[media_group_id]
            if media_group_id in self.media_group_tasks:
                del self.media_group_tasks[media_group_id]
    
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
    
    async def create_news_from_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, photo_files=None):
        """Create NewsPage from admin message (with optional photo(s))"""
        from .models import NewsPage, NewsImage, TelegramBotConfig, TelegramSyncLog
        from wagtail.models import Page
        from wagtail.images.models import Image
        from django.utils.text import slugify
        import re
        
        text = update.message.caption if photo_files else update.message.text
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
        
        # Strip all hashtags from text
        clean_text = re.sub(r'#\w+', '', text).strip()
        
        # Extract title from first line
        lines = clean_text.split('\n')
        title = lines[0][:100].strip() if lines else 'Telegram Post'
        if not title:
            title = f"Telegram {post_type.capitalize()} {message_id}"
        
        # Body = everything after the title line (no duplication)
        body_lines = [l.strip() for l in lines[1:] if l.strip()]
        body_text = '\n'.join(body_lines)
        
        # Excerpt from body (not title), max 200 chars
        excerpt = body_text[:200].strip() if body_text else title
        
        # Content as HTML paragraphs from body text
        if body_text:
            content_html = ''.join(f'<p>{line}</p>' for line in body_lines)
        else:
            content_html = ''
        
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
            
            # Handle images
            cover_image_id = None
            gallery_image_ids = []
            
            if photo_files:
                # Multiple photos - first is cover, rest are gallery
                if isinstance(photo_files, list):
                    for idx, photo_file in enumerate(photo_files):
                        img_id = await sync_to_async(self._save_telegram_image)(photo_file, f"{title} {idx+1}")
                        if img_id:
                            if idx == 0:
                                cover_image_id = img_id
                            gallery_image_ids.append(img_id)
                else:
                    # Single photo
                    cover_image_id = await sync_to_async(self._save_telegram_image)(photo_files, title)
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
                    content=content_html,
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
                
                # Add gallery images
                if gallery_image_ids:
                    for idx, img_id in enumerate(gallery_image_ids):
                        NewsImage.objects.create(
                            news=news_page,
                            image_id=img_id,
                            sort_order=idx
                        )
                
                # Create log
                TelegramSyncLog.objects.create(
                    telegram_message_id=message_id,
                    telegram_chat_id=chat_id,
                    news_page=news_page,
                    status='success',
                    raw_data={'text': text, 'photo_count': len(photo_files) if photo_files and isinstance(photo_files, list) else (1 if photo_files else 0)}
                )
                
                return news_page, config.auto_publish, len(gallery_image_ids)
            
            news_page, auto_publish, gallery_count = await create_and_publish()
            
            # Send success message
            type_emoji = "📰" if post_type == 'news' else "📢"
            status_text = "published ✅" if auto_publish else "saved as draft 📝"
            
            photo_text = ""
            if gallery_count > 0:
                photo_text = f"\n📸 Photos: {gallery_count}"
            elif photo_files:
                photo_text = "\n📸 Photo: 1"
            
            success_message = (
                f"{type_emoji} *{post_type.capitalize()} {status_text}!*\n\n"
                f"*Title:* {title}\n"
                f"*ID:* {news_page.id}"
                f"{photo_text}\n\n"
                "✨ Your post is now live on the website!"
            )
            
            await update.message.reply_text(
                success_message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error creating news: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def create_news_from_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create news from single photo message"""
        # Get the highest quality photo
        photo = update.message.photo[-1]
        
        # Download the photo
        photo_file = await photo.get_file()
        
        # Create news with photo
        await self.create_news_from_message(update, context, photo_files=photo_file)
    
    def _save_telegram_image(self, photo_file, title):
        """Save Telegram photo to Wagtail Image (sync function)"""
        from wagtail.images.models import Image
        import requests
        
        try:
            # Get the download URL
            file_url = getattr(photo_file, 'file_path', None)
            if not file_url:
                logger.error(f"No file_path for photo_file: {photo_file}")
                return None
            
            logger.info(f"Downloading image from: {file_url}")
            
            # Download photo
            response = requests.get(file_url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Downloaded image: {len(response.content)} bytes")
            
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
            
            logger.info(f"Saved Wagtail image ID: {wagtail_image.id}")
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
            is_admin = config.is_admin(user_id)
            logger.info(f"Admin check - User ID: {user_id}, Is Admin: {is_admin}")
            return is_admin
        
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
