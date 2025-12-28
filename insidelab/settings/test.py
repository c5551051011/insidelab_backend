"""
Test settings for InsideLab project.
This file contains settings specific to running tests.
"""

from .base import *

# Keep all apps for testing to avoid model relation errors
# INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'apps.publications']

# Use test URL configuration
ROOT_URLCONF = 'insidelab.urls_test'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Test Database Configuration (Use existing SQLite database)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Use existing database
        'TEST': {
            'NAME': BASE_DIR / 'test_db.sqlite3',  # Separate test database copy
        }
    }
}

# Disable cache during tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Test cache timeouts (not actually used with DummyCache, but defined for consistency)
CACHE_TIMEOUTS = {
    'UNIVERSITIES': 60 * 60 * 24,
    'DEPARTMENTS': 60 * 60 * 12,
    'PROFESSORS': 60 * 60 * 6,
    'LABS': 60 * 30,
    'REVIEWS': 60 * 15,
    'RESEARCH_GROUPS': 60 * 60 * 2,
    'USER_PROFILE': 60 * 30,
    'SEARCH_RESULTS': 60 * 10,
}

# CORS settings (permissive for tests)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Test email backend (console or in-memory)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable password validation for easier testing
AUTH_PASSWORD_VALIDATORS = []

# Site domain for tests
SITE_DOMAIN = 'testserver'

# Disable logging during tests to reduce noise
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['null'],
            'level': 'CRITICAL',
        },
    },
}

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for faster tests (optional)
# Uncomment if you want even faster tests
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

print("🧪 Test settings loaded")
