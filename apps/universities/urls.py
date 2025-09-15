
# apps/universities/urls.py
from rest_framework.routers import DefaultRouter
from .views import UniversityViewSet, ProfessorViewSet

router = DefaultRouter()
router.register(r'professors', ProfessorViewSet, basename='professor')
router.register(r'', UniversityViewSet, basename='university')

urlpatterns = router.urls

