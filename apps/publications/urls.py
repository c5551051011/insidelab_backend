# apps/publications/urls.py
from rest_framework.routers import DefaultRouter
from .views import (
    PublicationViewSet, AuthorViewSet, VenueViewSet,
    ResearchAreaViewSet, LabPublicationStatsViewSet,
    CollaborationViewSet
)

router = DefaultRouter()
router.register(r'publications', PublicationViewSet, basename='publication')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'research-areas', ResearchAreaViewSet, basename='research-area')
router.register(r'lab-stats', LabPublicationStatsViewSet, basename='lab-stats')
router.register(r'collaborations', CollaborationViewSet, basename='collaboration')

urlpatterns = router.urls