#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from django.core.mail import send_mail
from apps.authentication.utils import send_verification_email
from django.contrib.auth import get_user_model

User = get_user_model()

def test_email_sending():
    print("Testing email configuration...")

    # Test basic email sending
    try:
        send_mail(
            subject='Test Email from InsideLab',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['c5551051011@gmail.com'],
            fail_silently=False,
        )
        print("✅ Basic email test: SUCCESS")
    except Exception as e:
        print(f"❌ Basic email test: FAILED - {e}")
        return False

    # Test verification email (if user exists)
    try:
        # Try to find an existing user or create a test user
        user, created = User.objects.get_or_create(
            email='c5551051011@gmail.com',
            defaults={
                'username': 'testuser',
                'name': 'Test User',
                'position': 'Student'
            }
        )

        # Create a fake request object
        class FakeRequest:
            def build_absolute_uri(self, location):
                return f"http://127.0.0.1:8000{location}"

        fake_request = FakeRequest()

        email_sent = send_verification_email(user, fake_request)

        if email_sent:
            print("✅ Verification email test: SUCCESS")
        else:
            print("❌ Verification email test: FAILED - Email not sent")

    except Exception as e:
        print(f"❌ Verification email test: FAILED - {e}")

    print("\nEmail configuration:")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

if __name__ == '__main__':
    test_email_sending()