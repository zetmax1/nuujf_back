"""
Django management command to run the Telegram bot
Usage: python manage.py run_telegram_bot
"""
from django.core.management.base import BaseCommand
from news.models import TelegramBotConfig
from news.telegram_bot import UniversityNewsBot
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run the Telegram bot for University News'

    def add_arguments(self, parser):
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Use webhook mode instead of polling (requires webhook URL setup)',
        )

    def handle(self, *args, **options):
        """Run the bot"""
        
        # Get bot config from database
        try:
            config = TelegramBotConfig.objects.filter(is_active=True).first()
            
            if not config:
                self.stdout.write(
                    self.style.ERROR('No active Telegram bot configuration found!')
                )
                self.stdout.write('Please add a TelegramBotConfig in the admin panel.')
                return
            
            if not config.bot_token:
                self.stdout.write(
                    self.style.ERROR('Bot token not configured!')
                )
                self.stdout.write('Please add your bot token from @BotFather in the admin panel.')
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'Starting bot: {config.name}')
            )
            
            # Create and setup bot
            bot = UniversityNewsBot(config.bot_token)
            bot.setup()
            
            if options['webhook']:
                self.stdout.write(
                    self.style.WARNING('Webhook mode not fully implemented yet.')
                )
                self.stdout.write('Please use polling mode (default) for now.')
                return
            else:
                self.stdout.write('Running bot in polling mode...')
                self.stdout.write(
                    self.style.SUCCESS('✓ Bot is running! Press Ctrl+C to stop.')
                )
                bot.run_polling()
                
        except KeyboardInterrupt:
            self.stdout.write('\n' + self.style.SUCCESS('Bot stopped.'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running bot: {e}')
            )
            logger.exception('Bot error')
