#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from apps.labs.models import Lab
from apps.universities.models import Professor, UniversityDepartment

def test_api_creation():
    """Test how Lab creation works with the new university_department structure"""

    print("🧪 Testing Lab creation with university_department:")

    # Get a professor who has university_department
    professor = Professor.objects.filter(university_department__isnull=False).first()
    if not professor:
        print("❌ No professor with university_department found")
        return

    print(f"  Using professor: {professor.name}")
    print(f"  Professor's university_department: {professor.university_department}")

    # Test what happens when we create a Lab with just professor
    print("\n1. Creating Lab with just professor (should auto-set university_department):")
    lab_data = {
        'name': 'Test API Lab',
        'professor': professor,
        'description': 'Test lab created via API simulation'
    }

    try:
        # Simulate what happens in Lab.save()
        lab = Lab(**lab_data)
        print(f"  Before save - university_department: {lab.university_department}")
        lab.save()  # This should trigger our auto-population logic
        print(f"  ✅ After save - university_department: {lab.university_department}")
        print(f"  ✅ Legacy university: {lab.university}")
        print(f"  ✅ Legacy department: {lab.department}")

        # Clean up
        lab.delete()

    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\n2. Testing what API users need to provide:")
    print("  Required fields for API:")
    print("    - name: Lab name")
    print("    - professor: Professor ID")
    print("    - description: Lab description")
    print("  Auto-populated fields:")
    print("    - university_department: From professor.university_department")
    print("    - university: From professor.university_department.university (legacy)")
    print("    - department: From professor.university_department.department.name (legacy)")

if __name__ == "__main__":
    test_api_creation()