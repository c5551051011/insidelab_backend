from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = 'Create admin user for production'

    def handle(self, *args, **options):
        User = get_user_model()

        # Admin credentials from environment variables
        admin_username = config('ADMIN_USERNAME', default='admin')
        admin_email = config('ADMIN_EMAIL', default='admin@insidelab.io')
        admin_password = config('ADMIN_PASSWORD', default='insidelab2024!')

        # Check if admin user already exists
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{admin_username}" already exists.')
            )
            return

        # Create admin user
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user "{admin_username}"')
        )
        self.stdout.write(f'Username: {admin_username}')
        self.stdout.write(f'Email: {admin_email}')
        self.stdout.write(f'Password: {admin_password}')