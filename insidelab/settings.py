import os
from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'insidelab.up.railway.app', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',

    'apps.authentication',
    'apps.labs',
    'apps.reviews',
    'apps.universities',
    'apps.utils',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'insidelab.urls'

WSGI_APPLICATION = 'insidelab.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='postgres'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}

# Caching Configuration
# Detect Railway environment and Redis availability
IS_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ
REDIS_URL = config('REDIS_URL', default=None)

# Always try to use dummy cache to avoid Redis connection issues
# Until Redis service is properly configured on Railway
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Uncomment below when Redis service is added to Railway project
# if IS_RAILWAY and REDIS_URL:
#     # Production Redis configuration for Railway
#     CACHES = {
#         'default': {
#             'BACKEND': 'django_redis.cache.RedisCache',
#             'LOCATION': REDIS_URL,
#             'OPTIONS': {
#                 'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#                 'CONNECTION_POOL_KWARGS': {
#                     'retry_on_timeout': True,
#                     'socket_connect_timeout': 10,
#                     'socket_timeout': 10,
#                     'ssl_cert_reqs': None,
#                     'ssl_check_hostname': False,
#                 },
#                 'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
#                 'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
#             },
#             'KEY_PREFIX': 'insidelab',
#             'VERSION': 1,
#             'TIMEOUT': 300,
#         }
#     }
# elif not IS_RAILWAY:
#     # Local development Redis configuration
#     CACHES = {
#         'default': {
#             'BACKEND': 'django_redis.cache.RedisCache',
#             'LOCATION': 'redis://127.0.0.1:6379/1',
#             'OPTIONS': {
#                 'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#                 'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
#                 'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
#             },
#             'KEY_PREFIX': 'insidelab',
#             'VERSION': 1,
#             'TIMEOUT': 300,
#         }
#     }

# Railway-specific cache timeouts (shorter for memory efficiency)
if IS_RAILWAY:
    CACHE_TIMEOUTS = {
        'UNIVERSITIES': 60 * 60 * 6,       # 6 hours (reduced from 24)
        'DEPARTMENTS': 60 * 60 * 3,        # 3 hours (reduced from 12)
        'PROFESSORS': 60 * 60,             # 1 hour (reduced from 6)
        'LABS': 60 * 15,                   # 15 minutes (reduced from 30)
        'REVIEWS': 60 * 10,                # 10 minutes (reduced from 15)
        'RESEARCH_GROUPS': 60 * 60,        # 1 hour (reduced from 2)
        'USER_PROFILE': 60 * 15,           # 15 minutes (reduced from 30)
        'SEARCH_RESULTS': 60 * 5,          # 5 minutes (reduced from 10)
    }
else:
    # Development cache timeouts
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

# Cache configuration for sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
CORS_ALLOW_ALL_ORIGINS = True  # For development only - remove in production
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

# Add CORS allowed methods
CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Add preflight cache time
CORS_PREFLIGHT_MAX_AGE = 86400

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Email Configuration
# Use Resend for Railway compatibility (no SMTP port restrictions)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='apps.authentication.email_backends.ResendEmailBackend')

# Resend API Configuration
RESEND_API_KEY = config('RESEND_API_KEY', default='')

# Fallback SMTP Configuration (for local development)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Email From Address
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='InsideLab <noreply@insidelab.io>')

# Site Configuration for email links
SITE_DOMAIN = config('SITE_DOMAIN', default='localhost:8000')
