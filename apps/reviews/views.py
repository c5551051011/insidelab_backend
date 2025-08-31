
# apps/reviews/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import F
from .models import Review, ReviewHelpful
from .serializers import ReviewSerializer, ReviewHelpfulSerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'lab')
        
        # Filter by lab if specified
        lab_id = self.request.query_params.get('lab', None)
        if lab_id is not None:
            queryset = queryset.filter(lab_id=lab_id)
        
        # Order by helpful count and recency
        return queryset.order_by('-helpful_count', '-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def helpful(self, request, pk=None):
        """Mark a review as helpful or not helpful"""
        review = self.get_object()
        is_helpful = request.data.get('is_helpful', True)
        
        helpful_vote, created = ReviewHelpful.objects.update_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': is_helpful}
        )
        
        # Update helpful count
        helpful_count = ReviewHelpful.objects.filter(
            review=review,
            is_helpful=True
        ).count()
        review.helpful_count = helpful_count
        review.save()
        
        return Response({
            'helpful_count': review.helpful_count,
            'user_vote': is_helpful
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        """Get current user's reviews"""
        reviews = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

