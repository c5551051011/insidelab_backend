from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = 'Create admin user for production'

    def handle(self, *args, **options):
        import sys

        try:
            User = get_user_model()

            # Admin credentials from environment variables
            admin_username = config('ADMIN_USERNAME', default='admin')
            admin_email = config('ADMIN_EMAIL', default='insidelab.25@gmail.com')
            admin_password = config('ADMIN_PASSWORD', default='insidelab.25@gmail.com')

            self.stdout.write(f'🔍 [SIGNAL] Checking for admin user "{admin_username}"...')
            print(f'🔍 [SIGNAL] Checking for admin user "{admin_username}"...', file=sys.stderr)

            # Check if admin user already exists (by username or email)
            if User.objects.filter(username=admin_username).exists() or User.objects.filter(email=admin_email).exists():
                message = f'⚠️ [SIGNAL] Admin user "{admin_username}" or email "{admin_email}" already exists.'
                self.stdout.write(self.style.WARNING(message))
                print(message, file=sys.stderr)
                return

            # Create admin user
            self.stdout.write('🚀 [SIGNAL] Creating admin user...')
            print('🚀 [SIGNAL] Creating admin user...', file=sys.stderr)

            admin_user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )

            success_message = f'✅ Successfully created admin user "{admin_username}"'
            self.stdout.write(self.style.SUCCESS(success_message))
            print(success_message, file=sys.stderr)

            credentials = f'📋 Credentials: {admin_username} / {admin_password}'
            self.stdout.write(credentials)
            print(credentials, file=sys.stderr)

        except Exception as e:
            error_message = f'❌ [SIGNAL] Error creating admin user: {e}'
            self.stdout.write(self.style.ERROR(error_message))
            print(error_message, file=sys.stderr)
            # Don't raise exception in production to avoid crashing the app
            pass