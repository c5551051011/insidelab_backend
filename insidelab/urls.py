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
        description="API for graduate school lab reviews",
        terms_of_service="https://www.insidelab.com/terms/",
        contact=openapi.Contact(email="contact@insidelab.com"),
        license=openapi.License(name="BSD License"),
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
    ])),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
