

# apps/labs/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .models import Lab, ResearchTopic, Publication, RecruitmentStatus
from .serializers import (
    LabMinimalSerializer, LabListSerializer, LabDetailSerializer,
    ResearchTopicSerializer, PublicationSerializer,
    RecruitmentStatusSerializer
)
from .filters import LabFilter
from apps.utils.cache import cache_response, CacheManager

class LabViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LabFilter
    search_fields = ['name', 'professor__name', 'university__name', 'research_areas']
    ordering_fields = ['overall_rating', 'review_count', 'created_at', 'name', 'professor__name', 'university__name', 'lab_size']
    ordering = ['-overall_rating', '-review_count']
    
    def get_queryset(self):
        # Check for fields parameter to optimize queries
        fields = self.request.query_params.get('fields', 'full')

        if fields == 'minimal':
            # For minimal fields, only need professor name
            queryset = Lab.objects.select_related('professor')
        elif self.action == 'retrieve':
            # For detail view, prefetch all related data
            queryset = Lab.objects.select_related(
                'professor',
                'university',
                'university_department__university',
                'university_department__department',
                'research_group'
            ).prefetch_related(
                'research_topics',
                'recent_publications',
                'recruitment_status'
            )
        else:
            # For full list view, select related fields needed for list serializer
            queryset = Lab.objects.select_related(
                'professor',
                'university',
                'university_department__university',
                'university_department__department',
                'research_group'
            ).prefetch_related('recruitment_status')

        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LabDetailSerializer

        # Check for fields parameter to determine serializer
        fields = self.request.query_params.get('fields', 'full')
        if fields == 'minimal':
            return LabMinimalSerializer
        return LabListSerializer
    
    @cache_response('LABS', timeout=60*60)  # Cache for 1 hour
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured labs with high ratings and reviews"""
        featured_labs = self.get_queryset().filter(
            overall_rating__gte=4.5,
            review_count__gte=10
        )[:10]
        serializer = self.get_serializer(featured_labs, many=True)
        return Response(serializer.data)

    @cache_response('LABS', timeout=60*15)  # Cache for 15 minutes (recruiting status changes frequently)
    @action(detail=False, methods=['get'])
    def recruiting(self, request):
        """Get labs that are currently recruiting"""
        position = request.query_params.get('position', 'phd')

        recruiting_labs = self.get_queryset().filter(
            recruitment_status__isnull=False
        )

        if position == 'phd':
            recruiting_labs = recruiting_labs.filter(recruitment_status__is_recruiting_phd=True)
        elif position == 'postdoc':
            recruiting_labs = recruiting_labs.filter(recruitment_status__is_recruiting_postdoc=True)
        elif position == 'intern':
            recruiting_labs = recruiting_labs.filter(recruitment_status__is_recruiting_intern=True)

        page = self.paginate_queryset(recruiting_labs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recruiting_labs, many=True)
        return Response(serializer.data)

    @cache_response('LABS', timeout=60*30)  # Cache for 30 minutes
    @action(detail=False, methods=['get'])
    def by_research_group(self, request):
        """Get labs by research group"""
        research_group_id = request.query_params.get('research_group_id')

        if not research_group_id:
            return Response(
                {'error': 'research_group_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        labs = self.get_queryset().filter(research_group_id=research_group_id)

        page = self.paginate_queryset(labs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(labs, many=True)
        return Response(serializer.data)

