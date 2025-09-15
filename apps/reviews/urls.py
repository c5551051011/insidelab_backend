
# apps/reviews/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ReviewViewSet, get_review_categories

router = DefaultRouter()
router.register(r'', ReviewViewSet, basename='review')

urlpatterns = [
    path('categories/', get_review_categories, name='review_categories'),
] + router.urls