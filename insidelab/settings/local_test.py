"""
Local test settings for Swagger UI testing
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite for quick local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Dummy cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Simple CORS
CORS_ALLOW_ALL_ORIGINS = True

# Console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

print("🧪 Local test settings loaded for Swagger testing")
