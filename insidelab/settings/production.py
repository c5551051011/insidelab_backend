"""
Production settings for InsideLab project.
This file contains settings specific to production environment.
"""

from .base import *
from decouple import config
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Production hosts
ALLOWED_HOSTS = [
    'insidelab.up.railway.app',
    'healthcheck.railway.app',
    config('PRODUCTION_DOMAIN', default=''),
    'localhost',
]

# Production Database Configuration (Supabase) - No fallbacks
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('PROD_DB_NAME'),
        'USER': config('PROD_DB_USER'),
        'PASSWORD': config('PROD_DB_PASSWORD'),
        'HOST': config('PROD_DB_HOST'),
        'PORT': config('PROD_DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}


# Production Cache Configuration
REDIS_URL = config('REDIS_URL', default=None)

# Railway Redis detection
IS_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ
if IS_RAILWAY and not REDIS_URL:
    # Use Railway's internal Redis service
    REDIS_URL = 'redis://redis.railway.internal:6379'

if REDIS_URL:
    # Production Redis configuration
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'retry_on_timeout': True,
                    'socket_connect_timeout': 10,
                    'socket_timeout': 10,
                },
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            },
            'KEY_PREFIX': 'insidelab_prod',
            'VERSION': 1,
            'TIMEOUT': 300,
        }
    }
    print("✅ Production Redis cache enabled")
else:
    # Fallback to dummy cache if Redis is not available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    print("⚠️ Redis not configured, using DummyCache")

# Production cache timeouts (shorter for memory efficiency)
CACHE_TIMEOUTS = {
    'UNIVERSITIES': 60 * 60 * 6,       # 6 hours
    'DEPARTMENTS': 60 * 60 * 3,        # 3 hours
    'PROFESSORS': 60 * 60,             # 1 hour
    'LABS': 60 * 15,                   # 15 minutes
    'REVIEWS': 60 * 10,                # 10 minutes
    'RESEARCH_GROUPS': 60 * 60,        # 1 hour
    'USER_PROFILE': 60 * 15,           # 15 minutes
    'SEARCH_RESULTS': 60 * 5,          # 5 minutes
}

# Production CORS settings (more restrictive)
CORS_ALLOWED_ORIGINS = [
    "https://insidelab.io",
    "https://www.insidelab.io",
    "https://c5551051011.github.io",
    config('FRONTEND_URL', default=''),
]

# Filter out empty strings
CORS_ALLOWED_ORIGINS = [url for url in CORS_ALLOWED_ORIGINS if url]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Strict CORS in production

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

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000  # 1 year

# Only enable HTTPS redirect if not on Railway (Railway handles HTTPS)
# Check if RAILWAY_ENVIRONMENT exists (Railway sets this automatically)
railway_env = config('RAILWAY_ENVIRONMENT', default=None)
if railway_env is None:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'

# Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Production email configuration (uses Resend)
EMAIL_BACKEND = 'apps.authentication.email_backends.ResendEmailBackend'

# Site domain for production
SITE_DOMAIN = config('SITE_DOMAIN', default='insidelab.io')

# Additional production settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Disable browsable API in production
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
    ]

print("🚀 Production settings loaded")