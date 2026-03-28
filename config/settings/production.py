from .base import *


# WhiteNoise serves static files directly from Gunicorn with compression + caching.
# See https://whitenoise.readthedocs.io/en/latest/django.html
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"


try:
    from .local import *
except ImportError:
    pass
