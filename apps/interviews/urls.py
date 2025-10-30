# apps/interviews/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResearchAreaViewSet, InterviewViewSet

router = DefaultRouter()
router.register(r'research-areas', ResearchAreaViewSet, basename='research-area')
router.register(r'', InterviewViewSet, basename='interview')

app_name = 'interviews'

urlpatterns = [
    path('', include(router.urls)),
]
