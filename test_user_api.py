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
from apps.universities.models import UniversityDepartment

User = get_user_model()

def test_user_api():
    """Test User API with university_department"""

    print("🧪 Testing User API with university_department:")

    # Get a university department for testing
    university_department = UniversityDepartment.objects.first()
    if not university_department:
        print("❌ No university_department found")
        return

    print(f"  Using university_department: {university_department} (ID: {university_department.id})")

    # Create a test user with university_department
    test_user = User.objects.create_user(
        username="api_test_user",
        email="api_test@example.com",
        password="testpass123",
        name="API Test User",
        university_department=university_department,
        position="PhD Student",
        email_verified=True
    )

    # Get JWT token
    login_data = {
        "email": "api_test@example.com",
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
            test_user.delete()
            return
    except Exception as e:
        print(f"  ❌ Login error: {e}")
        test_user.delete()
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print("\n1. Testing User profile API:")
    try:
        # Get user profile
        profile_response = requests.get("http://localhost:8000/api/v1/auth/profile/", headers=headers)
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"  ✅ Profile retrieved successfully")
            print(f"  Profile fields: {list(profile_data.keys())}")
            print(f"  university_name: {profile_data.get('university_name')}")
            print(f"  university_department_name: {profile_data.get('university_department_name')}")
            print(f"  department_name: {profile_data.get('department_name')}")
            print(f"  department (legacy): {profile_data.get('department')}")
        else:
            print(f"  ❌ Profile request failed: {profile_response.text}")
    except Exception as e:
        print(f"  ❌ Profile request error: {e}")

    print("\n2. Testing User profile update:")
    try:
        # Update user profile with university_department
        update_data = {
            "name": "Updated API Test User",
            "position": "MS Student",
            "university_department": university_department.id
        }

        update_response = requests.patch("http://localhost:8000/api/v1/auth/profile/",
                                       json=update_data, headers=headers)
        if update_response.status_code == 200:
            updated_data = update_response.json()
            print(f"  ✅ Profile updated successfully")
            print(f"  Updated name: {updated_data.get('name')}")
            print(f"  Updated position: {updated_data.get('position')}")
            print(f"  university_department_name: {updated_data.get('university_department_name')}")
            print(f"  department_name: {updated_data.get('department_name')}")
        else:
            print(f"  ❌ Profile update failed: {update_response.text}")
    except Exception as e:
        print(f"  ❌ Profile update error: {e}")

    print("\n3. Testing registration with university_department:")
    try:
        # Test registration with university_department
        register_data = {
            "username": "new_dept_user",
            "email": "new_dept_user@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "name": "New Department User",
            "position": "PostDoc",
            "university_department": university_department.id
        }

        register_response = requests.post("http://localhost:8000/api/v1/auth/register/",
                                        json=register_data)
        if register_response.status_code == 201:
            register_result = register_response.json()
            print(f"  ✅ Registration successful")
            print(f"  New user ID: {register_result.get('id')}")

            # Clean up new user
            try:
                new_user = User.objects.get(email="new_dept_user@example.com")
                new_user.delete()
                print(f"  🧹 New user deleted")
            except User.DoesNotExist:
                pass
        else:
            print(f"  ❌ Registration failed: {register_response.text}")
    except Exception as e:
        print(f"  ❌ Registration error: {e}")

    # Clean up test user
    try:
        test_user.delete()
        print(f"  🧹 Test user deleted")
    except Exception as e:
        print(f"  ⚠️ Could not delete test user: {e}")

    print("\n✅ User API testing complete!")

if __name__ == "__main__":
    test_user_api()