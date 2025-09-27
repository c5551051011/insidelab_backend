#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.universities.models import UniversityDepartment
from apps.authentication.serializers import UserSerializer

User = get_user_model()

def test_user_department_changes():
    """Test User model changes with university_department"""

    print("🧪 Testing User model with university_department:")

    # Get a university department
    university_department = UniversityDepartment.objects.first()
    if not university_department:
        print("❌ No university_department found")
        return

    print(f"  Using university_department: {university_department}")

    # Test user creation with university_department
    print("\n1. Creating User with university_department:")
    user_data = {
        'username': 'test_dept_user',
        'email': 'test_dept@example.com',
        'password': 'testpass123',
        'name': 'Test Department User',
        'university_department': university_department,
        'position': 'PhD Student'
    }

    try:
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            name=user_data['name'],
            university_department=user_data['university_department'],
            position=user_data['position']
        )

        print(f"  ✅ User created: {user.email}")
        print(f"  Before save - university: {user.university}")
        print(f"  Before save - department: {user.department}")
        print(f"  university_department: {user.university_department}")

        # Save to trigger auto-population
        user.save()

        print(f"  ✅ After save - university: {user.university}")
        print(f"  ✅ After save - department: {user.department}")
        print(f"  ✅ verification_badge: {user.verification_badge}")

        print("\n2. Testing User serializer:")
        serializer = UserSerializer(user)
        data = serializer.data

        print(f"  Serializer data keys: {list(data.keys())}")
        print(f"  university_name: {data.get('university_name')}")
        print(f"  university_department_name: {data.get('university_department_name')}")
        print(f"  department_name: {data.get('department_name')}")
        print(f"  department (legacy): {data.get('department')}")

        # Clean up
        user.delete()
        print(f"  🧹 Test user deleted")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n3. Testing user creation without university_department:")
    try:
        # Create user without university_department
        user2 = User.objects.create_user(
            username='test_no_dept',
            email='test_no_dept@example.com',
            password='testpass123',
            name='Test No Dept User',
            position='MS Student'
        )

        print(f"  ✅ User created without department: {user2.email}")
        print(f"  university: {user2.university}")
        print(f"  university_department: {user2.university_department}")
        print(f"  department: {user2.department}")
        print(f"  verification_badge: {user2.verification_badge}")

        # Test serializer
        serializer2 = UserSerializer(user2)
        data2 = serializer2.data
        print(f"  university_department_name: {data2.get('university_department_name')}")
        print(f"  department_name: {data2.get('department_name')}")

        # Clean up
        user2.delete()
        print(f"  🧹 Test user 2 deleted")

    except Exception as e:
        print(f"  ❌ Error creating user without department: {e}")

    print("\n✅ User department testing complete!")

if __name__ == "__main__":
    test_user_department_changes()