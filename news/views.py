import json
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import NewsPage, TelegramBotConfig, TelegramSyncLog
from .serializers import NewsPageListSerializer, NewsPageDetailSerializer

logger = logging.getLogger(__name__)


@extend_schema(tags=['News & Announcements'])
class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for university news and announcements.
    
    Provides listing, detail view, and filtering capabilities.
    All content supports multilingual content.
    """
    queryset = NewsPage.objects.live().public()
    serializer_class = NewsPageDetailSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NewsPageListSerializer
        return NewsPageDetailSerializer
    
    @extend_schema(
        summary="List all news and announcements",
        description="Retrieve a paginated list of all published news and announcements.",
        parameters=[
            OpenApiParameter(
                name='locale',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code (uz, en, ru)',
                required=False,
                examples=[
                    OpenApiExample('Uzbek', value='uz'),
                    OpenApiExample('English', value='en'),
                    OpenApiExample('Russian', value='ru'),
                ]
            ),
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by post type: news or announcement',
                required=False,
                examples=[
                    OpenApiExample('News only', value='news'),
                    OpenApiExample('Announcements only', value='announcement'),
                ]
            ),
        ],
        responses={200: NewsPageListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get news/announcement detail",
        description="Retrieve detailed information about a specific news item including gallery images.",
        responses={200: NewsPageDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only increment view count once per session per post
        viewed_posts = request.session.get('viewed_posts', [])
        if instance.pk not in viewed_posts:
            instance.views_count += 1
            instance.save(update_fields=['views_count'])
            viewed_posts.append(instance.pk)
            request.session['viewed_posts'] = viewed_posts
        
        return super().retrieve(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by locale/language (optional - if not specified, return all)
        locale = self.request.query_params.get('locale')
        if locale:
            queryset = queryset.filter(locale__language_code=locale)
        
        # Filter by post type
        post_type = self.request.query_params.get('type')
        if post_type in ['news', 'announcement']:
            queryset = queryset.filter(post_type=post_type)
        
        # Order: pinned first, then by date
        queryset = queryset.order_by('-is_pinned', '-published_date')
        
        # Prefetch gallery images for detail view
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('gallery_images')
        
        return queryset
    
    @extend_schema(
        summary="Get pinned items",
        description="Retrieve all pinned/featured news and announcements.",
        responses={200: NewsPageListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pinned(self, request):
        """Get pinned items: /api/news/pinned/"""
        queryset = NewsPage.objects.live().public().filter(is_pinned=True)
        
        # Filter by locale if specified
        locale = request.query_params.get('locale')
        if locale:
            queryset = queryset.filter(locale__language_code=locale)
        
        queryset = queryset.order_by('-published_date')
        serializer = NewsPageListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get announcements only",
        description="Retrieve only announcements (e'lonlar).",
        parameters=[
            OpenApiParameter(
                name='locale',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code (uz, en, ru)',
                required=False,
            ),
        ],
        responses={200: NewsPageListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def announcements(self, request):
        """Get announcements: /api/news/announcements/"""
        queryset = NewsPage.objects.live().public().filter(post_type='announcement')
        
        # Filter by locale if specified
        locale = request.query_params.get('locale')
        if locale:
            queryset = queryset.filter(locale__language_code=locale)
        
        queryset = queryset.order_by('-is_pinned', '-published_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NewsPageListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = NewsPageListSerializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    """
    Webhook endpoint for Telegram bot.
    Receives messages from Telegram channel and creates NewsPage entries.
    """
    authentication_classes = []
    permission_classes = []
    
    @extend_schema(
        summary="Telegram Webhook",
        description="Endpoint for receiving Telegram bot updates. Do not call directly.",
        request={
            'application/json': {
                'type': 'object',
                'description': 'Telegram Update object'
            }
        },
        responses={200: {'description': 'OK'}}
    )
    def post(self, request):
        try:
            # Get active bot config
            config = TelegramBotConfig.objects.filter(is_active=True).first()
            if not config:
                logger.warning("No active Telegram bot configuration found")
                return Response({'status': 'no_config'}, status=status.HTTP_200_OK)
            
            # Parse the update
            update = request.data
            logger.info(f"Received Telegram update: {json.dumps(update, indent=2)}")
            
            # Handle channel posts
            message = update.get('channel_post') or update.get('message')
            if not message:
                return Response({'status': 'no_message'}, status=status.HTTP_200_OK)
            
            message_id = message.get('message_id')
            chat_id = message.get('chat', {}).get('id')
            
            # Check for duplicates
            if TelegramSyncLog.objects.filter(
                telegram_message_id=message_id,
                telegram_chat_id=chat_id
            ).exists():
                logger.info(f"Duplicate message {message_id} from chat {chat_id}")
                return Response({'status': 'duplicate'}, status=status.HTTP_200_OK)
            
            # Process the message
            result = self._process_message(message, config)
            
            return Response({'status': result}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing Telegram webhook: {str(e)}", exc_info=True)
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_200_OK)
    
    def _process_message(self, message, config):
        """Process a Telegram message and create NewsPage"""
        from wagtail.models import Page
        from django.utils import timezone
        from django.utils.text import slugify
        import re
        
        message_id = message.get('message_id')
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text') or message.get('caption') or ''
        
        # Determine post type from hashtags
        text_lower = text.lower()
        post_type = 'news'  # default
        
        for hashtag in config.get_announcement_hashtags():
            if hashtag in text_lower:
                post_type = 'announcement'
                break
        
        # Strip hashtags from text
        clean_text = re.sub(r'#\w+', '', text).strip()
        
        # Extract title (first line)
        lines = clean_text.split('\n')
        title = lines[0][:100].strip() if lines else 'Telegram Post'
        if not title:
            title = f"Telegram {post_type.capitalize()} {message_id}"
        
        # Body = everything after title line
        body_lines = [l.strip() for l in lines[1:] if l.strip()]
        body_text = '\n'.join(body_lines)
        
        # Excerpt from body, max 200 chars
        excerpt = body_text[:200].strip() if body_text else title
        
        # Content as HTML paragraphs
        if body_text:
            content_html = ''.join(f'<p>{line}</p>' for line in body_lines)
        else:
            content_html = ''
        
        # Find parent page (NewsIndexPage)
        try:
            parent_page = Page.objects.filter(
                slug='news'
            ).first() or Page.objects.filter(
                content_type__model='newsindexpage'
            ).first()
            
            if not parent_page:
                # Create log entry for error
                TelegramSyncLog.objects.create(
                    telegram_message_id=message_id,
                    telegram_chat_id=chat_id,
                    status='failed',
                    error_message='No NewsIndexPage found',
                    raw_data=message
                )
                return 'no_parent_page'
            
        except Exception as e:
            logger.error(f"Error finding parent page: {e}")
            return 'error_parent_page'
        
        # Create the news page
        try:
            # Generate unique slug
            base_slug = slugify(title[:50]) or f'telegram-{message_id}'
            slug = base_slug
            counter = 1
            while NewsPage.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
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
            
            # Add as child of parent page
            if config.auto_publish:
                parent_page.add_child(instance=news_page)
                news_page.save_revision().publish()
            else:
                parent_page.add_child(instance=news_page)
                news_page.unpublish()
            
            # Create success log
            TelegramSyncLog.objects.create(
                telegram_message_id=message_id,
                telegram_chat_id=chat_id,
                news_page=news_page,
                status='success',
                raw_data=message
            )
            
            logger.info(f"Created NewsPage '{title}' from Telegram message {message_id}")
            return 'created'
            
        except Exception as e:
            logger.error(f"Error creating NewsPage: {e}", exc_info=True)
            TelegramSyncLog.objects.create(
                telegram_message_id=message_id,
                telegram_chat_id=chat_id,
                status='failed',
                error_message=str(e),
                raw_data=message
            )
            return 'error_creating'
