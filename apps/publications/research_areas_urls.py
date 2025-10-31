# apps/publications/research_areas_urls.py
from rest_framework.routers import DefaultRouter
from .views import ResearchAreaViewSet

router = DefaultRouter()
router.register(r'', ResearchAreaViewSet, basename='research-area')

urlpatterns = router.urls