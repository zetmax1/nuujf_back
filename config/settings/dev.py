from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-kz#%6dz1-1j89^w^t)6!n$k_5qnf+5iz2m5rc%(wn1j5gmbws+"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

if DEBUG:
    # django-silk: request/query profiler — dev only, never in production
    INSTALLED_APPS += ['silk']
    MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE
    SILKY_PYTHON_PROFILER = False  # True only when profiling CPU
    SILKY_ANALYZE_QUERIES = True
    # Exclude Wagtail admin to suppress JS-parsing warnings
    SILKY_INTERCEPT_FUNC = lambda request: not request.path.startswith('/admin/')

try:
    from .local import *
except ImportError:
    pass
