#!/usr/bin/env python
"""
Research Group 조회 방법 예제들
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from apps.universities.models import University, ResearchGroup, UniversityDepartment
from apps.universities.serializers import ResearchGroupSerializer

def get_research_groups_examples():
    """Research Group 조회 방법들"""

    print("🔍 Research Group 조회 방법들\n")

    # 1. University로 조회
    print("1️⃣ University로 Research Group 조회:")
    try:
        purdue = University.objects.get(name__icontains='Purdue')
        rgs_by_university = ResearchGroup.objects.filter(
            university_department__university=purdue
        ).select_related('university_department__university', 'university_department__department')

        print(f"   Purdue University Research Groups: {rgs_by_university.count()}개")
        for rg in rgs_by_university[:3]:
            print(f"   📚 {rg.name}")
            print(f"      🏛️ {rg.university_department.department.name}")
            print()
    except University.DoesNotExist:
        print("   ❌ Purdue University not found")

    # 2. Department로 조회
    print("2️⃣ Department로 Research Group 조회:")
    rgs_by_dept = ResearchGroup.objects.filter(
        university_department__department__name__icontains='Computer Science'
    ).select_related('university_department__university', 'university_department__department')

    print(f"   Computer Science Research Groups: {rgs_by_dept.count()}개")
    for rg in rgs_by_dept[:3]:
        print(f"   📚 {rg.name}")
        print(f"      🏫 {rg.university_department.university.name}")
        print()

    # 3. University + Department로 조회
    print("3️⃣ University + Department로 Research Group 조회:")
    try:
        purdue = University.objects.get(name__icontains='Purdue')
        rgs_specific = ResearchGroup.objects.filter(
            university_department__university=purdue,
            university_department__department__name__icontains='Computer Science'
        ).select_related('university_department__university', 'university_department__department')

        print(f"   Purdue CS Research Groups: {rgs_specific.count()}개")
        for rg in rgs_specific[:5]:
            print(f"   📚 {rg.name}")
            print(f"      🔬 Areas: {rg.research_areas}")
            print()
    except University.DoesNotExist:
        print("   ❌ University not found")

    # 4. Research Areas로 필터링
    print("4️⃣ Research Areas로 필터링:")
    ai_rgs = ResearchGroup.objects.filter(
        research_areas__icontains='Machine Learning'
    ).select_related('university_department__university', 'university_department__department')

    print(f"   Machine Learning Research Groups: {ai_rgs.count()}개")
    for rg in ai_rgs[:3]:
        print(f"   📚 {rg.name}")
        print(f"      🏫 {rg.university_department.university.name}")
        print(f"      🏛️ {rg.university_department.department.name}")
        print()

    # 5. Serializer 사용 예제
    print("5️⃣ Serializer로 JSON 응답 생성:")
    sample_rgs = ResearchGroup.objects.filter(
        university_department__university=purdue
    )[:2]

    serializer = ResearchGroupSerializer(sample_rgs, many=True)
    print("   📄 JSON 응답 예제:")
    import json
    print(json.dumps(serializer.data[0], indent=2, ensure_ascii=False)[:500] + "...")

def api_usage_examples():
    """API 사용 예제들"""

    print("\n\n🌐 API 사용 예제들\n")

    base_url = "https://insidelab.up.railway.app/api/v1/universities/research-groups/"

    examples = [
        {
            "desc": "모든 Research Group 조회",
            "url": base_url,
            "note": "페이지네이션 적용됨"
        },
        {
            "desc": "특정 University의 Research Group 조회",
            "url": f"{base_url}?university_department__university=17",
            "note": "Purdue University (ID: 17)"
        },
        {
            "desc": "특정 Department의 Research Group 조회",
            "url": f"{base_url}?university_department__department=2",
            "note": "Computer Science (ID: 2)"
        },
        {
            "desc": "University + Department 조합 조회",
            "url": f"{base_url}?university_department__university=17&university_department__department=2",
            "note": "Purdue University + Computer Science"
        },
        {
            "desc": "Research Areas로 검색",
            "url": f"{base_url}?search=Machine Learning",
            "note": "검색 기능 사용"
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"{i}️⃣ {example['desc']}:")
        print(f"   📡 GET {example['url']}")
        print(f"   💡 {example['note']}")
        print()

    print("🔧 사용 가능한 필터 파라미터:")
    print("   - university_department__university: University ID")
    print("   - university_department__department: Department ID")
    print("   - search: 이름, 설명, 연구분야로 검색")
    print("   - ordering: 정렬 (name, created_at, professor_count, lab_count)")

if __name__ == "__main__":
    get_research_groups_examples()
    api_usage_examples()