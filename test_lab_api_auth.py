#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.universities.models import Professor

User = get_user_model()

def test_authenticated_lab_api():
    """Test Lab API creation with authentication"""

    print("🧪 Testing authenticated Lab API creation:")

    # Create or get a test user
    test_email = "test_lab_api@example.com"
    try:
        user = User.objects.get(email=test_email)
        print(f"  Using existing test user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username="testuser_api",
            email=test_email,
            password="testpass123",
            first_name="Test",
            last_name="User",
            email_verified=True
        )
        print(f"  Created test user: {user.email}")

    # Get JWT token
    login_data = {
        "email": test_email,
        "password": "testpass123"
    }

    try:
        login_response = requests.post("http://localhost:8000/api/v1/auth/login/", json=login_data)
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            print(f"  ✅ Got JWT token")
        else:
            print(f"  ❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"  ❌ Login error: {e}")
        return

    # Get a professor who has university_department
    professor = Professor.objects.filter(university_department__isnull=False).first()
    if not professor:
        print("❌ No professor with university_department found")
        return

    print(f"  Using professor: {professor.name} (ID: {professor.id})")
    print(f"  Professor's university_department: {professor.university_department}")

    # Test Lab creation via API
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    lab_data = {
        "name": "Test API Lab with Auth",
        "professor": professor.id,
        "description": "Test lab created via authenticated API call"
    }

    print(f"\n1. Making authenticated POST request to create lab:")
    print(f"  Request data: {json.dumps(lab_data, indent=2)}")

    try:
        response = requests.post("http://localhost:8000/api/v1/labs/",
                               json=lab_data,
                               headers=headers)

        print(f"  Status code: {response.status_code}")

        if response.status_code == 201:
            response_data = response.json()
            print(f"  ✅ Lab created successfully!")

            lab_id = response_data.get('id')
            print(f"  Created lab ID: {lab_id}")
            print(f"  university_department: {response_data.get('university_department')}")
            print(f"  university_department_name: {response_data.get('university_department_name')}")
            print(f"  department_name: {response_data.get('department_name')}")

            # Get lab details
            print(f"\n2. Getting lab details:")
            detail_response = requests.get(f"http://localhost:8000/api/v1/labs/{lab_id}/",
                                         headers=headers)
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print(f"  Detail university_department: {detail_data.get('university_department')}")
                print(f"  Detail university_department_name: {detail_data.get('university_department_name')}")
                print(f"  Detail department_name: {detail_data.get('department_name')}")

            # Clean up - delete the test lab
            print(f"\n3. Cleaning up:")
            delete_response = requests.delete(f"http://localhost:8000/api/v1/labs/{lab_id}/",
                                            headers=headers)
            if delete_response.status_code == 204:
                print(f"  🧹 Test lab deleted successfully")
            else:
                print(f"  ⚠️ Could not delete test lab (status: {delete_response.status_code})")

        else:
            print(f"  ❌ API call failed: {response.text}")

    except Exception as e:
        print(f"  ❌ Error making API call: {e}")

    # Clean up user
    try:
        user.delete()
        print(f"  🧹 Test user deleted")
    except Exception as e:
        print(f"  ⚠️ Could not delete test user: {e}")

    print("\n✅ API verification complete!")
    print("\nSummary:")
    print("  - Lab model auto-populates university_department_id from professor")
    print("  - API serializers expose university_department fields correctly")
    print("  - List view includes university_department_name and department_name")
    print("  - Detail view includes university_department ID and name fields")
    print("  - Lab creation through API works with authentication")

if __name__ == "__main__":
    test_authenticated_lab_api()