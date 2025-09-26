#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from apps.universities.models import Professor

def test_lab_api():
    """Test Lab API creation with university_department_id"""

    print("🧪 Testing Lab API creation with university_department_id:")

    # Get a professor who has university_department
    professor = Professor.objects.filter(university_department__isnull=False).first()
    if not professor:
        print("❌ No professor with university_department found")
        return

    print(f"  Using professor: {professor.name} (ID: {professor.id})")
    print(f"  Professor's university_department: {professor.university_department}")

    # Test API endpoint
    api_url = "http://localhost:8000/api/v1/labs/"
    lab_data = {
        "name": "Test API Lab via HTTP",
        "professor": professor.id,
        "description": "Test lab created via actual API call"
    }

    print(f"\n1. Making POST request to {api_url}")
    print(f"  Request data: {json.dumps(lab_data, indent=2)}")

    try:
        response = requests.post(api_url, json=lab_data)
        print(f"  Status code: {response.status_code}")

        if response.status_code == 201:
            response_data = response.json()
            print(f"  ✅ Lab created successfully!")
            print(f"  Response data: {json.dumps(response_data, indent=2)}")

            # Check if university_department_id is set
            lab_id = response_data.get('id')
            if lab_id:
                # Get the lab details to see university_department_id
                detail_response = requests.get(f"{api_url}{lab_id}/")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    university_department_id = detail_data.get('university_department')
                    print(f"  ✅ University department ID: {university_department_id}")

                    # Clean up - delete the test lab
                    delete_response = requests.delete(f"{api_url}{lab_id}/")
                    if delete_response.status_code == 204:
                        print(f"  🧹 Test lab deleted successfully")
                    else:
                        print(f"  ⚠️ Could not delete test lab (status: {delete_response.status_code})")
                else:
                    print(f"  ❌ Could not get lab details (status: {detail_response.status_code})")
        else:
            print(f"  ❌ API call failed: {response.text}")

    except Exception as e:
        print(f"  ❌ Error making API call: {e}")

    print("\n2. Testing serializer fields:")
    print("  Checking what fields are exposed in the API response...")

    # Test what fields are available in list view
    try:
        list_response = requests.get(api_url)
        if list_response.status_code == 200:
            list_data = list_response.json()
            if list_data.get('results'):
                sample_lab = list_data['results'][0]
                print(f"  List view fields: {list(sample_lab.keys())}")
                if 'university_department' in sample_lab:
                    print(f"  ✅ university_department is exposed in list view")
                else:
                    print(f"  ⚠️ university_department is NOT exposed in list view")

        # Test detail view
        if list_data.get('results'):
            lab_id = list_data['results'][0]['id']
            detail_response = requests.get(f"{api_url}{lab_id}/")
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print(f"  Detail view fields: {list(detail_data.keys())}")
                if 'university_department' in detail_data:
                    print(f"  ✅ university_department is exposed in detail view: {detail_data.get('university_department')}")
                else:
                    print(f"  ⚠️ university_department is NOT exposed in detail view")
    except Exception as e:
        print(f"  ❌ Error checking serializer fields: {e}")

if __name__ == "__main__":
    test_lab_api()