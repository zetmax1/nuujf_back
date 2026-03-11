import os
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'News & Announcements'

    def ready(self):
        """Auto-start Telegram bot in dev mode when TELEGRAM_BOT_ENABLED=true"""
        # Only start if explicitly enabled via env var
        if os.environ.get('TELEGRAM_BOT_ENABLED', '').lower() != 'true':
            return

        # In dev mode, Django's auto-reloader spawns 2 processes.
        # RUN_MAIN is set only in the child (reloader) process, so we
        # start the bot only there to avoid running it twice.
        if os.environ.get('RUN_MAIN') != 'true':
            return

        import threading

        def _start_bot():
            """Start the telegram bot in a background thread"""
            import time
            # Give Django time to fully initialize
            time.sleep(2)

            try:
                from news.models import TelegramBotConfig
                from news.telegram_bot import UniversityNewsBot

                config = TelegramBotConfig.objects.filter(is_active=True).first()

                if not config:
                    logger.info("Telegram bot: No active config found, skipping auto-start")
                    return

                if not config.bot_token:
                    logger.warning("Telegram bot: No token configured, skipping auto-start")
                    return

                logger.info(f"Starting Telegram bot '{config.name}' in background thread...")
                bot = UniversityNewsBot(config.bot_token)
                bot.setup()
                bot.run_polling()

            except Exception as e:
                logger.error(f"Telegram bot auto-start failed: {e}", exc_info=True)

        thread = threading.Thread(target=_start_bot, daemon=True)
        thread.start()
        logger.info("Telegram bot thread spawned (waiting for Django to finish init...)")
