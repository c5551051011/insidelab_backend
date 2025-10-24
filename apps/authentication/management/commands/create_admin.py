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

            self.stdout.write('🔍 Checking for existing admin user...')
            print('🔍 Checking for existing admin user...', file=sys.stderr)

            # Check if admin user already exists
            if User.objects.filter(username=admin_username).exists():
                message = f'⚠️  Admin user "{admin_username}" already exists.'
                self.stdout.write(self.style.WARNING(message))
                print(message, file=sys.stderr)
                return

            # Create admin user
            self.stdout.write('🚀 Creating new admin user...')
            print('🚀 Creating new admin user...', file=sys.stderr)

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
            error_message = f'❌ Error creating admin user: {e}'
            self.stdout.write(self.style.ERROR(error_message))
            print(error_message, file=sys.stderr)
            raise