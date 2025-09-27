#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from apps.universities.models import University, UniversityDepartment

def test_departments_endpoint():
    """Test the new /universities/{id}/departments/ endpoint"""

    print("🧪 Testing /universities/{id}/departments/ endpoint:")

    # Get a university that has departments
    university_with_depts = University.objects.filter(
        university_departments__isnull=False
    ).first()

    if not university_with_depts:
        print("❌ No university with departments found")
        return

    print(f"  Testing with university: {university_with_depts.name} (ID: {university_with_depts.id})")

    # Check how many departments this university has
    dept_count = UniversityDepartment.objects.filter(university=university_with_depts, is_active=True).count()
    print(f"  University has {dept_count} active departments")

    # Test the API endpoint
    try:
        url = f"http://localhost:8000/api/v1/universities/{university_with_depts.id}/departments/"
        print(f"  Making request to: {url}")

        response = requests.get(url)
        print(f"  Status code: {response.status_code}")

        if response.status_code == 200:
            departments = response.json()
            print(f"  ✅ Endpoint working! Returned {len(departments)} departments")

            if departments:
                print("  Sample department data:")
                sample_dept = departments[0]
                print(f"    ID: {sample_dept.get('id')}")
                print(f"    Department name: {sample_dept.get('department_name')}")
                print(f"    Local name: {sample_dept.get('local_name')}")
                print(f"    Display name: {sample_dept.get('display_name')}")
                print(f"    Website: {sample_dept.get('website')}")
                print(f"    Head name: {sample_dept.get('head_name')}")
                print(f"    Is active: {sample_dept.get('is_active')}")

                print("\n  All departments for this university:")
                for dept in departments:
                    display_name = dept.get('display_name') or dept.get('department_name')
                    print(f"    - {display_name}")
        else:
            print(f"  ❌ Request failed: {response.text}")

    except Exception as e:
        print(f"  ❌ Error making request: {e}")

    # Test with a few more universities
    print(f"\n🧪 Testing with other universities:")

    # Test with universities 14, 17, 18 (the ones mentioned in the error)
    test_university_ids = [14, 17, 18]

    for uni_id in test_university_ids:
        try:
            university = University.objects.get(id=uni_id)
            url = f"http://localhost:8000/api/v1/universities/{uni_id}/departments/"

            response = requests.get(url)
            if response.status_code == 200:
                departments = response.json()
                print(f"  ✅ University {uni_id} ({university.name}): {len(departments)} departments")
            else:
                print(f"  ❌ University {uni_id}: Failed with status {response.status_code}")

        except University.DoesNotExist:
            print(f"  ⚠️ University {uni_id}: Does not exist")
        except Exception as e:
            print(f"  ❌ University {uni_id}: Error - {e}")

    print(f"\n✅ Department endpoint testing complete!")

if __name__ == "__main__":
    test_departments_endpoint()