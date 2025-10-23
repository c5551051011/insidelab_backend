"""
Swagger schema definitions for Universities APIs
"""
from drf_yasg import openapi

# University schemas
university_minimal_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'country': openapi.Schema(type=openapi.TYPE_STRING),
        'city': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

university_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='대학교명'),
        'country': openapi.Schema(type=openapi.TYPE_STRING, description='국가'),
        'state': openapi.Schema(type=openapi.TYPE_STRING, description='주/도'),
        'city': openapi.Schema(type=openapi.TYPE_STRING, description='도시'),
        'website': openapi.Schema(type=openapi.TYPE_STRING, description='웹사이트'),
        'ranking': openapi.Schema(type=openapi.TYPE_INTEGER, description='랭킹'),
        'logo_url': openapi.Schema(type=openapi.TYPE_STRING, description='로고 URL'),
    }
)

# Department schemas
department_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'department_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='학과명 (신규 생성 또는 기존 학과 사용)'
        ),
        'department': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='기존 학과 ID (department_name 대신 사용 가능)'
        ),
        'local_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='대학별 학과명 (선택사항)'
        ),
        'description': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='학과 설명 (department_name 사용 시만)'
        ),
        'website': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='학과 웹사이트'
        ),
        'head_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='학과장 이름'
        ),
    }
)

department_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'common_names': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
    }
)

# Professor schemas
professor_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='교수명'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='이메일'),
        'university_department': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='소속 학과'
        ),
        'research_group': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='연구 그룹'
        ),
        'research_interests': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='연구 관심분야'
        ),
        'profile_url': openapi.Schema(type=openapi.TYPE_STRING, description='프로필 URL'),
        'google_scholar_url': openapi.Schema(type=openapi.TYPE_STRING, description='Google Scholar URL'),
    }
)

# Research Group schemas
research_group_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'university_department'],
    properties={
        'name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='연구 그룹명'
        ),
        'university_department': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='소속 대학-학과 ID'
        ),
        'description': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='연구 그룹 설명'
        ),
        'website': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='웹사이트'
        ),
        'research_areas': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='연구 분야'
        ),
    }
)

research_group_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'website': openapi.Schema(type=openapi.TYPE_STRING),
        'research_areas': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING)
        ),
        'professor_count': openapi.Schema(type=openapi.TYPE_INTEGER),
        'lab_count': openapi.Schema(type=openapi.TYPE_INTEGER),
    }
)

# Common error response
error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지'),
    }
)
