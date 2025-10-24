from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'

    def ready(self):
        """Called when the app is ready"""
        post_migrate.connect(create_admin_user, sender=self)


@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    """Create admin user after migrations are applied"""
    # Only run for our authentication app to avoid multiple executions
    if sender.name != 'apps.authentication':
        return

    from django.contrib.auth import get_user_model
    from decouple import config
    import logging
    import sys

    logger = logging.getLogger(__name__)

    try:
        User = get_user_model()

        # Admin credentials
        admin_username = config('ADMIN_USERNAME', default='admin')
        admin_email = config('ADMIN_EMAIL', default='insidelab.25@gmail.com')
        admin_password = config('ADMIN_PASSWORD', default='insidelab.25@gmail.com')

        print(f'🔍 [SIGNAL] Checking for admin user "{admin_username}"...', file=sys.stderr)
        logger.info(f'Checking for admin user "{admin_username}"')

        # Check if admin user already exists
        if User.objects.filter(username=admin_username).exists():
            message = f'⚠️ [SIGNAL] Admin user "{admin_username}" already exists.'
            logger.info(message)
            print(message, file=sys.stderr)
            return

        # Create admin user
        print(f'🚀 [SIGNAL] Creating admin user "{admin_username}"...', file=sys.stderr)
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )

        success_message = f'✅ [SIGNAL] Admin user created: {admin_username} / {admin_password}'
        logger.info(success_message)
        print(success_message, file=sys.stderr)

    except Exception as e:
        error_message = f'❌ [SIGNAL] Error creating admin user: {e}'
        logger.error(error_message)
        print(error_message, file=sys.stderr)