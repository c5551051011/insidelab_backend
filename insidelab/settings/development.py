"""
Development settings for InsideLab project.
This file contains settings specific to development environment.
"""

from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Development Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', default='insidelab_dev'),
        'USER': os.getenv('DB_USER', default='postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', default='localhost'),
        'PORT': os.getenv('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}

# Development Cache Configuration
try:
    import redis
    # Test Redis connection
    r = redis.Redis(host='127.0.0.1', port=6379, db=1)
    r.ping()
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            },
            'KEY_PREFIX': 'insidelab_dev',
            'VERSION': 1,
            'TIMEOUT': 300,
        }
    }
    print("✅ Redis cache enabled for development")
except Exception as e:
    print(f"⚠️ Redis not available, using DummyCache: {e}")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Development cache timeouts (longer for development convenience)
CACHE_TIMEOUTS = {
    'UNIVERSITIES': 60 * 60 * 24,      # 24 hours
    'DEPARTMENTS': 60 * 60 * 12,       # 12 hours
    'PROFESSORS': 60 * 60 * 6,         # 6 hours
    'LABS': 60 * 30,                   # 30 minutes
    'REVIEWS': 60 * 15,                # 15 minutes
    'RESEARCH_GROUPS': 60 * 60 * 2,    # 2 hours
    'USER_PROFILE': 60 * 30,           # 30 minutes
    'SEARCH_RESULTS': 60 * 10,         # 10 minutes
}

# CORS settings for development (more permissive)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:9999",  # Flutter web default port
    "http://127.0.0.1:9999",
    "http://localhost:56768",  # Common Flutter web port
    "http://127.0.0.1:56768",
    "http://localhost:49152",  # Another common port
    "http://127.0.0.1:49152",
    "http://localhost:8000",  # Local Django dev
    "http://127.0.0.1:8000",
    "http://localhost:4000",  # Additional Flutter ports
    "http://127.0.0.1:4000",
    "http://localhost:37785",  # Random Flutter port
    "http://127.0.0.1:37785",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # For development only

CORS_ALLOWED_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_PREFLIGHT_MAX_AGE = 86400

# Development logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Development email backend (console for testing)
if not config('RESEND_API_KEY', default=''):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development specific settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# Site domain for development
SITE_DOMAIN = config('SITE_DOMAIN', default='localhost:8000')

print("🔧 Development settings loaded")