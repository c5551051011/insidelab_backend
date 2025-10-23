"""
Swagger schema definitions for Authentication APIs
"""
from drf_yasg import openapi

# Register API
register_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'username', 'password', 'password2'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='사용자 이메일 (로그인 ID로 사용)',
            format='email'
        ),
        'username': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='사용자명 (고유해야 함)',
            min_length=3,
            max_length=150
        ),
        'password': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='비밀번호',
            format='password',
            min_length=8
        ),
        'password2': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='비밀번호 확인',
            format='password'
        ),
        'name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='실명 (선택)'
        ),
        'university_email': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='대학 이메일 (선택)',
            format='email'
        ),
        'position': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='직위/신분',
            enum=['PhD Student', 'MS Student', 'Undergrad', 'PostDoc', 'Research Assistant', 'faculty']
        ),
    }
)

register_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'user': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        'email_sent': openapi.Schema(type=openapi.TYPE_BOOLEAN)
    }
)

# Login API
login_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='사용자 이메일',
            format='email'
        ),
        'password': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='비밀번호',
            format='password'
        ),
    }
)

login_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='JWT Access Token'
        ),
        'refresh': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='JWT Refresh Token'
        ),
        'user': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            }
        )
    }
)

# Google Auth
google_auth_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'id_token': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

# Feedback
feedback_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'subject', 'message'],
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='연락받을 이메일'
        ),
        'name': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='이름 (선택)'
        ),
        'subject': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='제목'
        ),
        'message': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='내용'
        ),
    }
)

# Common responses
error_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지'),
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False)
    }
)

success_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='성공 메시지'),
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True)
    }
)
