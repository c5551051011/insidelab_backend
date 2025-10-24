
# apps/universities/urls.py
from rest_framework.routers import DefaultRouter
from .views import UniversityViewSet, ResearchGroupViewSet

router = DefaultRouter()
router.register(r'research-groups', ResearchGroupViewSet, basename='researchgroup')
router.register(r'', UniversityViewSet, basename='university')

urlpatterns = router.urls

