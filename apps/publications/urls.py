# apps/publications/urls.py
from rest_framework.routers import DefaultRouter
from .views import (
    PublicationViewSet, AuthorViewSet, VenueViewSet,
    ResearchAreaViewSet, LabPublicationStatsViewSet,
    CollaborationViewSet
)

router = DefaultRouter()
router.register(r'', PublicationViewSet, basename='publication')  # Empty prefix for main endpoint
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'research-areas', ResearchAreaViewSet, basename='research-area')
router.register(r'lab-stats', LabPublicationStatsViewSet, basename='lab-stats')
router.register(r'collaborations', CollaborationViewSet, basename='collaboration')

urlpatterns = router.urls