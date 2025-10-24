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

    logger = logging.getLogger(__name__)

    try:
        User = get_user_model()

        # Admin credentials
        admin_username = config('ADMIN_USERNAME', default='admin')
        admin_email = config('ADMIN_EMAIL', default='insidelab.25@gmail.com')
        admin_password = config('ADMIN_PASSWORD', default='insidelab.25@gmail.com')

        # Check if admin user already exists
        if User.objects.filter(username=admin_username).exists():
            logger.info(f'Admin user "{admin_username}" already exists.')
            return

        # Create admin user
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )

        logger.info(f'Successfully created admin user "{admin_username}"')
        print(f'✅ Admin user created: {admin_username} / {admin_password}')

    except Exception as e:
        logger.error(f'Error creating admin user: {e}')
        print(f'❌ Error creating admin user: {e}')