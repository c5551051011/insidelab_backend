#!/usr/bin/env python
import os
import django
import sys

# Add the project root to the path
sys.path.append('/Users/jjin.choi/Desktop/_project/insidelab/backend')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from apps.authentication.utils import send_verification_email

User = get_user_model()

def test_email_verification():
    print("Testing email verification...")

    # Create a test user
    test_email = "test.email.verification@gmail.com"

    # Delete existing test user if exists
    User.objects.filter(email=test_email).delete()

    # Create new test user
    user = User.objects.create_user(
        email=test_email,
        username="testemail",
        name="Test Email User",
        password="testpass123"
    )

    print(f"Created test user: {user.email}")

    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'localhost:8000'

    # Test email sending
    try:
        result = send_verification_email(user, request)
        print(f"Email sending result: {result}")

        if result:
            print("✅ Email verification test PASSED!")
            print(f"Verification token: {user.email_verification_token}")
        else:
            print("❌ Email verification test FAILED!")

    except Exception as e:
        print(f"❌ Email verification test ERROR: {str(e)}")

    # Clean up
    user.delete()
    print("Test user cleaned up.")

if __name__ == "__main__":
    test_email_verification()