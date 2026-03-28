from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-kz#%6dz1-1j89^w^t)6!n$k_5qnf+5iz2m5rc%(wn1j5gmbws+"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

if DEBUG:
    from decouple import config as decouple_config
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': decouple_config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        }
    }

try:
    from .local import *
except ImportError:
    pass
