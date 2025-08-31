
# apps/labs/urls.py
from rest_framework.routers import DefaultRouter
from .views import LabViewSet

router = DefaultRouter()
router.register(r'', LabViewSet, basename='lab')

urlpatterns = router.urls

