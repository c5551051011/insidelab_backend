"""
Swagger schema definitions for Labs APIs
"""
from drf_yasg import openapi

# Lab schemas
lab_minimal_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'professor_name': openapi.Schema(type=openapi.TYPE_STRING),
        'overall_rating': openapi.Schema(type=openapi.TYPE_NUMBER),
    }
)

lab_list_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='연구실명'),
        'professor': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='지도교수 정보'
        ),
        'university_department': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='소속 학과'
        ),
        'research_group': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='연구 그룹'
        ),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='연구실 설명'),
        'website': openapi.Schema(type=openapi.TYPE_STRING, description='웹사이트'),
        'lab_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='랩 인원 수'),
        'research_areas': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='연구 분야'
        ),
        'overall_rating': openapi.Schema(type=openapi.TYPE_NUMBER, description='전체 평점'),
        'review_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='리뷰 수'),
        'recruitment_status': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='모집 현황'
        ),
    }
)

lab_detail_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='연구실명'),
        'professor': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='지도교수 상세 정보'
        ),
        'university_department': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='소속 학과'
        ),
        'research_group': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='연구 그룹'
        ),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='연구실 설명'),
        'website': openapi.Schema(type=openapi.TYPE_STRING, description='웹사이트'),
        'lab_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='랩 인원 수'),
        'research_areas': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='연구 분야'
        ),
        'tags': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='태그'
        ),
        'overall_rating': openapi.Schema(type=openapi.TYPE_NUMBER, description='전체 평점'),
        'review_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='리뷰 수'),
        'research_topics': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT),
            description='연구 주제'
        ),
        'recent_publications': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT),
            description='최근 논문'
        ),
        'recruitment_status': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='모집 현황'
        ),
    }
)

# Research Topic schemas
research_topic_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['title', 'description'],
    properties={
        'title': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='연구 주제 제목'
        ),
        'description': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='연구 주제 설명'
        ),
        'keywords': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='키워드'
        ),
        'funding_info': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='펀딩 정보'
        ),
    }
)

# Publication schemas
publication_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['title', 'venue', 'year'],
    properties={
        'title': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='논문 제목'
        ),
        'authors': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='저자 목록'
        ),
        'venue': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='학회/저널명'
        ),
        'year': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='출판 연도'
        ),
        'url': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='논문 URL'
        ),
        'abstract': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='초록'
        ),
        'citations': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='인용 수'
        ),
    }
)

# Recruitment Status schemas
recruitment_status_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'is_recruiting_phd': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='박사과정 모집 여부'
        ),
        'is_recruiting_postdoc': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='포닥 모집 여부'
        ),
        'is_recruiting_intern': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='인턴 모집 여부'
        ),
        'notes': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='모집 관련 메모'
        ),
    }
)

recruitment_status_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'is_recruiting_phd': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_recruiting_postdoc': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'is_recruiting_intern': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'notes': openapi.Schema(type=openapi.TYPE_STRING),
        'last_updated': openapi.Schema(
            type=openapi.TYPE_STRING,
            format='date-time'
        ),
    }
)

# Query parameters
fields_param = openapi.Parameter(
    'fields',
    openapi.IN_QUERY,
    description='응답 필드 수준 (minimal: 최소 필드만, full: 전체 필드)',
    type=openapi.TYPE_STRING,
    enum=['minimal', 'full'],
    default='full'
)

position_param = openapi.Parameter(
    'position',
    openapi.IN_QUERY,
    description='모집 포지션 (phd, postdoc, intern)',
    type=openapi.TYPE_STRING,
    enum=['phd', 'postdoc', 'intern'],
    default='phd'
)

research_group_id_param = openapi.Parameter(
    'research_group_id',
    openapi.IN_QUERY,
    description='연구 그룹 ID',
    type=openapi.TYPE_INTEGER,
    required=True
)

# Common error response
error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지'),
    }
)
