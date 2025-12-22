
# apps/labs/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LabViewSet, RecruitmentStatusViewSet

router = DefaultRouter()
router.register(r'', LabViewSet, basename='lab')

# Separate router for recruitment status
recruitment_router = DefaultRouter()
recruitment_router.register(r'', RecruitmentStatusViewSet, basename='recruitment')

urlpatterns = [
    path('recruitment/', include(recruitment_router.urls)),
] + router.urls

