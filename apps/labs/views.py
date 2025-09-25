

# apps/labs/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from .models import Lab, ResearchTopic, Publication, RecruitmentStatus
from .serializers import (
    LabListSerializer, LabDetailSerializer,
    ResearchTopicSerializer, PublicationSerializer,
    RecruitmentStatusSerializer
)
from .filters import LabFilter

class LabViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LabFilter
    search_fields = ['name', 'professor__name', 'university__name', 'research_areas']
    ordering_fields = ['overall_rating', 'review_count', 'created_at', 'name', 'professor__name', 'university__name', 'lab_size']
    ordering = ['-overall_rating', '-review_count']
    
    def get_queryset(self):
        queryset = Lab.objects.select_related('professor', 'university')
        
        # Add prefetch for detail view
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'research_topics',
                'recent_publications',
                'recruitment_status'
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LabDetailSerializer
        return LabListSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured labs with high ratings and reviews"""
        featured_labs = self.get_queryset().filter(
            overall_rating__gte=4.5,
            review_count__gte=10
        )[:10]
        serializer = self.get_serializer(featured_labs, many=True)
        return Response(serializer.data)
    
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

