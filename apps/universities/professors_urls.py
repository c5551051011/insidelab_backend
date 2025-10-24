# apps/universities/professors_urls.py
from rest_framework.routers import DefaultRouter
from .views import ProfessorViewSet

router = DefaultRouter()
router.register(r'', ProfessorViewSet, basename='professor')

urlpatterns = router.urls