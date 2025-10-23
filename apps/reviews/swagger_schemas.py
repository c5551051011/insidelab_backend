"""
Swagger schema definitions for Reviews APIs
"""
from drf_yasg import openapi

# Review schemas
review_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['lab', 'overall_experience', 'category_ratings'],
    properties={
        'lab': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='연구실 ID'
        ),
        'overall_experience': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='전체 경험 요약'
        ),
        'pros': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='장점'
        ),
        'cons': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='단점'
        ),
        'advice': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='조언'
        ),
        'category_ratings': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'category': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='평가 카테고리 ID'
                    ),
                    'rating': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='평점 (1-5)',
                        minimum=1.0,
                        maximum=5.0
                    ),
                }
            ),
            description='카테고리별 평점 목록'
        ),
        'is_anonymous': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='익명 리뷰 여부',
            default=True
        ),
    }
)

review_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'lab': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='연구실 정보'
        ),
        'user': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='작성자 정보'
        ),
        'overall_experience': openapi.Schema(type=openapi.TYPE_STRING),
        'pros': openapi.Schema(type=openapi.TYPE_STRING),
        'cons': openapi.Schema(type=openapi.TYPE_STRING),
        'advice': openapi.Schema(type=openapi.TYPE_STRING),
        'rating': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            description='전체 평점 (카테고리 평균)'
        ),
        'category_ratings': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT),
            description='카테고리별 평점'
        ),
        'helpful_count': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='도움됨 투표 수'
        ),
        'is_anonymous': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'status': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='리뷰 상태 (active, hidden, flagged)'
        ),
        'created_at': openapi.Schema(
            type=openapi.TYPE_STRING,
            format='date-time'
        ),
        'updated_at': openapi.Schema(
            type=openapi.TYPE_STRING,
            format='date-time'
        ),
    }
)

# Helpful vote schemas
helpful_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'is_helpful': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='도움됨 여부 (true: 도움됨, false: 도움안됨)',
            default=True
        ),
    }
)

helpful_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'helpful_count': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='전체 도움됨 투표 수'
        ),
        'user_vote': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='현재 사용자의 투표'
        ),
    }
)

# Rating Category schemas
rating_category_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='카테고리 이름 (내부용)'
        ),
        'display_name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='표시용 카테고리 이름'
        ),
        'description': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='카테고리 설명'
        ),
        'sort_order': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='정렬 순서'
        ),
    }
)

# Lab rating averages schemas
lab_rating_averages_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'lab_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'lab_name': openapi.Schema(type=openapi.TYPE_STRING),
        'overall_stats': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'overall_rating': openapi.Schema(type=openapi.TYPE_NUMBER),
                'total_reviews': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        'category_averages': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='카테고리별 평균 평점',
            additional_properties=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'average': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'review_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'category_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'category_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'last_updated': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format='date-time'
                    ),
                }
            )
        ),
        'is_precomputed': openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description='사전 계산된 데이터 여부'
        ),
    }
)

# Compare labs schemas
compare_labs_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'comparison': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='연구실별 비교 데이터',
            additional_properties=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'lab_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'overall_rating': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'total_reviews': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'category_averages': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'average': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'review_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                            }
                        )
                    ),
                }
            )
        ),
        'is_precomputed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    }
)

# Query parameters
lab_id_param = openapi.Parameter(
    'lab',
    openapi.IN_QUERY,
    description='연구실 ID로 필터링',
    type=openapi.TYPE_INTEGER
)

lab_ids_param = openapi.Parameter(
    'lab_ids',
    openapi.IN_QUERY,
    description='비교할 연구실 ID 목록 (여러 개 가능)',
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_INTEGER),
    required=True,
    collection_format='multi'
)

# Common error response
error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지'),
    }
)
