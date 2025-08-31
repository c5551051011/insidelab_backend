
# apps/universities/urls.py
from rest_framework.routers import DefaultRouter
from .views import UniversityViewSet, ProfessorViewSet

router = DefaultRouter()
router.register(r'', UniversityViewSet)
router.register(r'professors', ProfessorViewSet)

urlpatterns = router.urls

