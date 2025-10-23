"""
Test URL configuration for InsideLab project.
Excludes problematic apps for testing.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/universities/', include('apps.universities.urls')),
    path('api/universities/', include('apps.universities.department_urls')),
    path('api/labs/', include('apps.labs.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    # publications excluded for testing
]
