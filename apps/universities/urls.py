
# apps/universities/urls.py
from rest_framework.routers import DefaultRouter
from .views import UniversityViewSet, ProfessorViewSet, ResearchGroupViewSet

router = DefaultRouter()
router.register(r'research-groups', ResearchGroupViewSet, basename='researchgroup')
router.register(r'professors', ProfessorViewSet, basename='professor')
router.register(r'', UniversityViewSet, basename='university')

urlpatterns = router.urls

