# insidelab/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

def health_check(request):
    """Health check endpoint for Railway"""
    return JsonResponse({"status": "healthy", "environment": settings.DJANGO_ENVIRONMENT if hasattr(settings, 'DJANGO_ENVIRONMENT') else "unknown"})

schema_view = get_schema_view(
    openapi.Info(
        title="InsideLab API",
        default_version='v1',
        description="""
# InsideLab API Documentation

대학원 연구실 리뷰 및 정보 공유 플랫폼 API

## 주요 기능

### 🔐 인증 (Authentication)
- JWT 기반 사용자 인증
- Google OAuth 2.0 소셜 로그인
- 대학 이메일 인증
- 회원가입 및 로그인

### 🏫 대학 정보 (Universities)
- 대학 목록 및 상세 정보
- 학과 정보
- 교수 프로필
- 연구 그룹

### 🔬 연구실 (Labs)
- 연구실 목록 및 검색
- 연구실 상세 정보
- 논문 정보
- 모집 현황

### ⭐ 리뷰 (Reviews)
- 다차원 평가 시스템
- 리뷰 작성 및 조회
- 도움됨 투표
- 카테고리별 평점

### 📚 논문 (Publications)
- 논문 검색
- 저자 정보
- 인용 수

## 인증 방법

대부분의 API는 JWT 토큰 인증이 필요합니다.

```
Authorization: Bearer <access_token>
```

## 응답 형식

모든 API는 JSON 형식으로 응답합니다.

## 에러 코드

- 200: 성공
- 201: 생성 성공
- 400: 잘못된 요청
- 401: 인증 필요
- 403: 권한 없음
- 404: 리소스 없음
- 500: 서버 오류
        """,
        terms_of_service="https://www.insidelab.com/terms/",
        contact=openapi.Contact(email="contact@insidelab.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include([
        path('auth/', include('apps.authentication.urls')),
        path('universities/', include('apps.universities.urls')),
        path('departments/', include('apps.universities.department_urls')),
        path('labs/', include('apps.labs.urls')),
        path('publications/', include('apps.publications.urls')),
        path('reviews/', include('apps.reviews.urls')),
        path('health/', health_check, name='health-check'),

        # API Documentation under /api/v1/
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-docs'),
    ])),

    # Root level documentation (for convenience)
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
