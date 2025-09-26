#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from apps.labs.models import Lab
from apps.universities.models import Professor
from apps.labs.serializers import LabListSerializer, LabDetailSerializer

def test_lab_creation_logic():
    """Test Lab creation logic that would be used by API"""

    print("🧪 Testing Lab creation logic (simulating API):")

    # Get a professor who has university_department
    professor = Professor.objects.filter(university_department__isnull=False).first()
    if not professor:
        print("❌ No professor with university_department found")
        return

    print(f"  Using professor: {professor.name} (ID: {professor.id})")
    print(f"  Professor's university_department: {professor.university_department}")

    print("\n1. Testing Lab creation with just professor (simulating API POST):")

    # Create lab data similar to what API would receive
    lab_data = {
        'name': 'Test API Lab Logic',
        'professor': professor,
        'description': 'Test lab created to verify API logic'
    }

    try:
        # Create the lab instance (this is what the serializer would do)
        lab = Lab(**lab_data)
        print(f"  Before save - university_department: {lab.university_department}")

        # Save the lab (this triggers our auto-population logic)
        lab.save()
        print(f"  ✅ After save - university_department: {lab.university_department}")
        print(f"  ✅ Auto-populated university: {lab.university}")
        print(f"  ✅ Auto-populated department: {lab.department}")

        print("\n2. Testing serializers with the created lab:")

        # Test LabListSerializer
        list_serializer = LabListSerializer(lab)
        list_data = list_serializer.data
        print(f"  List serializer fields: {list(list_data.keys())}")
        print(f"  university_department in list: {list_data.get('university_department')}")
        print(f"  university_department_name: {list_data.get('university_department_name')}")
        print(f"  department_name: {list_data.get('department_name')}")

        # Test LabDetailSerializer
        detail_serializer = LabDetailSerializer(lab)
        detail_data = detail_serializer.data
        print(f"  Detail serializer university_department: {detail_data.get('university_department')}")
        print(f"  Detail serializer university_department_name: {detail_data.get('university_department_name')}")
        print(f"  Detail serializer department_name: {detail_data.get('department_name')}")

        # Clean up
        lab.delete()
        print(f"  🧹 Test lab deleted")

    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\n3. Testing API endpoint responses (read-only):")
    try:
        # Test list endpoint
        response = requests.get("http://localhost:8000/api/v1/labs/")
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                sample_lab = data['results'][0]
                print(f"  List API now includes: {list(sample_lab.keys())}")
                if 'university_department' in sample_lab:
                    print(f"  ✅ university_department in list API: {sample_lab.get('university_department')}")
                if 'university_department_name' in sample_lab:
                    print(f"  ✅ university_department_name in list API: {sample_lab.get('university_department_name')}")
                if 'department_name' in sample_lab:
                    print(f"  ✅ department_name in list API: {sample_lab.get('department_name')}")

                # Test detail endpoint
                lab_id = sample_lab['id']
                detail_response = requests.get(f"http://localhost:8000/api/v1/labs/{lab_id}/")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(f"  Detail API university_department: {detail_data.get('university_department')}")
                    print(f"  Detail API university_department_name: {detail_data.get('university_department_name')}")
                    print(f"  Detail API department_name: {detail_data.get('department_name')}")
        else:
            print(f"  ❌ Could not access API: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error accessing API: {e}")

if __name__ == "__main__":
    test_lab_creation_logic()