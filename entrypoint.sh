#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL..."
while ! python -c "
import socket, sys, os
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((os.environ.get('DB_HOST', 'db'), int(os.environ.get('DB_PORT', '5432'))))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

echo "⏳ Waiting for Redis..."
while ! python -c "
import socket, sys, os
from urllib.parse import urlparse
redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/1')
parsed = urlparse(redis_url)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((parsed.hostname or 'redis', parsed.port or 6379))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  sleep 1
done
echo "✅ Redis is ready!"

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "👤 Creating default superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='zokhidjon').exists():
    User.objects.create_superuser('zokhidjon', 'zokhidjonyuta@gmail.com', '(yuta0011)!')
    print('✅ Superuser created: zokhidjon')
else:
    print('✅ Superuser already exists.')
"

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🚀 Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8086 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
