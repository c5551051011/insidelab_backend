import os
from django.core.wsgi import get_wsgi_application

# Environment-based settings selection
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings.development')

application = get_wsgi_application()