
# apps/reviews/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import F, Avg
from django.shortcuts import get_object_or_404
from .models import Review, ReviewHelpful, RatingCategory, ReviewRating
from .serializers import ReviewSerializer, ReviewHelpfulSerializer, RatingCategorySerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'lab').prefetch_related(
            'category_ratings__category'
        )

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


class RatingCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for rating categories - read-only for API consumers"""
    serializer_class = RatingCategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return RatingCategory.objects.filter(is_active=True).order_by('sort_order')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_review_categories(request):
    """Get available review categories for rating labs"""
    categories = RatingCategory.objects.filter(is_active=True).order_by('sort_order')
    category_names = [cat.display_name for cat in categories]

    return Response({
        'categories': category_names,
        'count': len(category_names)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_lab_rating_averages(request, lab_id):
    """Get precomputed category-wise rating averages for a specific lab"""
    from apps.labs.models import Lab, LabCategoryAverage

    try:
        lab = get_object_or_404(Lab, id=lab_id)

        # Get precomputed averages
        lab_averages = LabCategoryAverage.objects.filter(
            lab=lab
        ).select_related('category').filter(category__is_active=True).order_by('category__sort_order')

        averages = {}
        for avg_record in lab_averages:
            averages[avg_record.category.display_name] = {
                'average': float(avg_record.average_rating),
                'review_count': avg_record.review_count,
                'category_id': avg_record.category.id,
                'category_name': avg_record.category.name,
                'last_updated': avg_record.last_updated.isoformat()
            }

        # Get overall lab stats
        overall_stats = {
            'overall_rating': float(lab.overall_rating),
            'total_reviews': lab.review_count
        }

        return Response({
            'lab_id': lab_id,
            'lab_name': lab.name,
            'overall_stats': overall_stats,
            'category_averages': averages,
            'is_precomputed': True  # Flag to indicate this is using precomputed data
        })

    except Exception as e:
        return Response(
            {'error': f'Failed to get lab averages: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def compare_labs_averages(request):
    """Compare multiple labs by their category averages"""
    from apps.labs.models import Lab, LabCategoryAverage

    # Get lab IDs from query params
    lab_ids = request.GET.getlist('lab_ids')
    if not lab_ids:
        return Response(
            {'error': 'Please provide lab_ids as query parameters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Convert to integers
        lab_ids = [int(lab_id) for lab_id in lab_ids]
    except ValueError:
        return Response(
            {'error': 'Invalid lab_ids format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get labs and their precomputed averages efficiently
        labs = Lab.objects.filter(id__in=lab_ids).prefetch_related(
            'category_averages__category'
        )

        comparison_data = {}
        for lab in labs:
            lab_data = {
                'lab_name': lab.name,
                'overall_rating': float(lab.overall_rating),
                'total_reviews': lab.review_count,
                'category_averages': {}
            }

            # Get category averages for this lab
            for avg_record in lab.category_averages.filter(category__is_active=True):
                lab_data['category_averages'][avg_record.category.display_name] = {
                    'average': float(avg_record.average_rating),
                    'review_count': avg_record.review_count
                }

            comparison_data[lab.id] = lab_data

        return Response({
            'comparison': comparison_data,
            'is_precomputed': True
        })

    except Exception as e:
        return Response(
            {'error': f'Failed to compare labs: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

