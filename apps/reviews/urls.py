
# apps/reviews/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ReviewViewSet, RatingCategoryViewSet, get_review_categories,
    get_lab_rating_averages, compare_labs_averages
)

router = DefaultRouter()
router.register(r'rating-categories', RatingCategoryViewSet, basename='rating-category')
router.register(r'', ReviewViewSet, basename='review')

urlpatterns = [
    path('categories/', get_review_categories, name='review_categories'),
    path('lab/<int:lab_id>/averages/', get_lab_rating_averages, name='lab_rating_averages'),
    path('labs/compare/', compare_labs_averages, name='compare_labs_averages'),
] + router.urls