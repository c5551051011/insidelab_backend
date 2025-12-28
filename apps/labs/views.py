

# apps/labs/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .models import Lab, ResearchTopic, Publication, RecruitmentStatus
from .serializers import (
    LabMinimalSerializer, LabCompactSerializer, LabListSerializer, LabDetailSerializer, LabDetailMinimalSerializer,
    ResearchTopicSerializer, PublicationSerializer,
    RecruitmentStatusSerializer
)
from .filters import LabFilter
from apps.utils.cache import cache_response, CacheManager
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .swagger_schemas import recruitment_status_request, recruitment_status_response, error_response

class LabViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LabFilter
    search_fields = ['name', 'head_professor__name', 'university__name', 'research_areas']
    ordering_fields = ['overall_rating', 'review_count', 'created_at', 'name', 'head_professor__name', 'university__name', 'lab_size']
    ordering = ['-overall_rating', '-review_count']
    
    def get_queryset(self):
        # Check for fields parameter to optimize queries
        fields = self.request.query_params.get('fields', 'full')

        if fields == 'minimal':
            # For minimal fields, only need head professor name
            queryset = Lab.objects.select_related(
                'head_professor',
                'university',
                'university_department__university',
                'university_department__department',
                'research_group',
            )
        elif fields == 'compact':
            # For compact fields, need university, head_professor, and department info
            queryset = Lab.objects.select_related(
                'head_professor',
                'university',
                'university_department__department'
            )
        elif self.action == 'retrieve':
            # For detail view, prefetch all related data
            queryset = Lab.objects.select_related(
                'head_professor',
                'university',
                'university_department__university',
                'university_department__department',
                'research_group'
            ).prefetch_related(
                'research_topics',
                'recent_publications__authors',
                'recent_publications__venues',
                'recent_publications__research_areas',
                'recent_publications__labs',
                'recruitment_status',
                'professors'  # Reverse relationship from Professor.lab
            )
        else:
            # For full list view, select related fields needed for list serializer
            queryset = Lab.objects.select_related(
                'head_professor',
                'university',
                'university_department__university',
                'university_department__department',
                'research_group'
            ).prefetch_related('recruitment_status', 'professors')

        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            if self.request.query_params.get('fields') == 'minimal':
                return LabDetailMinimalSerializer
            return LabDetailSerializer

        # Check for fields parameter to determine serializer
        fields = self.request.query_params.get('fields', 'full')
        if fields == 'minimal':
            return LabMinimalSerializer
        elif fields == 'compact':
            return LabCompactSerializer
        return LabListSerializer

    @cache_response('LABS', timeout=60 * 15)
    def retrieve(self, request, *args, **kwargs):
        """Cache lab detail responses for 15 minutes"""
        return super().retrieve(request, *args, **kwargs)
    
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


class RecruitmentStatusViewSet(viewsets.ModelViewSet):
    """
    연구실 모집 현황 관리 API

    연구실의 모집 현황(PhD, Postdoc, Intern)을 독립적으로 관리할 수 있는 API입니다.
    Lab 전체를 수정하지 않고 모집 현황만 업데이트할 수 있습니다.

    ## 엔드포인트
    - 목록 조회: GET /api/v1/labs/recruitment/
    - 상세 조회: GET /api/v1/labs/recruitment/{lab_id}/
    - 생성: POST /api/v1/labs/recruitment/
    - 전체 수정: PUT /api/v1/labs/recruitment/{lab_id}/
    - 부분 수정: PATCH /api/v1/labs/recruitment/{lab_id}/
    - 삭제: DELETE /api/v1/labs/recruitment/{lab_id}/

    ## 필터링
    - ?recruiting_phd=true : PhD 모집 중인 연구실만
    - ?recruiting_postdoc=true : Postdoc 모집 중인 연구실만
    - ?recruiting_intern=true : Intern 모집 중인 연구실만
    """
    queryset = RecruitmentStatus.objects.select_related(
        'lab',
        'lab__head_professor',
        'lab__university',
        'lab__university_department__university'
    ).all()
    serializer_class = RecruitmentStatusSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'lab_id'  # Use lab_id instead of pk for easier access

    def get_queryset(self):
        """Optionally filter by recruiting status"""
        queryset = super().get_queryset()

        # Filter by position type if provided
        recruiting_phd = self.request.query_params.get('recruiting_phd')
        recruiting_postdoc = self.request.query_params.get('recruiting_postdoc')
        recruiting_intern = self.request.query_params.get('recruiting_intern')

        if recruiting_phd is not None:
            queryset = queryset.filter(is_recruiting_phd=recruiting_phd.lower() == 'true')
        if recruiting_postdoc is not None:
            queryset = queryset.filter(is_recruiting_postdoc=recruiting_postdoc.lower() == 'true')
        if recruiting_intern is not None:
            queryset = queryset.filter(is_recruiting_intern=recruiting_intern.lower() == 'true')

        return queryset

    @swagger_auto_schema(
        operation_summary="모집 현황 생성",
        operation_description="새로운 연구실의 모집 현황을 생성합니다.",
        request_body=recruitment_status_request,
        responses={
            201: openapi.Response('생성 성공', recruitment_status_response),
            400: openapi.Response('잘못된 요청', error_response),
            401: openapi.Response('인증 필요'),
        }
    )
    def create(self, request, *args, **kwargs):
        """Create recruitment status for a lab"""
        lab_id = request.data.get('lab_id') or request.data.get('lab')

        if not lab_id:
            return Response(
                {'error': 'lab_id or lab field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if lab exists
        lab = get_object_or_404(Lab, id=lab_id)

        # Check if recruitment status already exists
        if hasattr(lab, 'recruitment_status'):
            return Response(
                {'error': 'Recruitment status already exists for this lab. Use PUT or PATCH to update.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clear cache when creating
        CacheManager.invalidate_lab_caches(lab_id)

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="모집 현황 전체 수정",
        operation_description="연구실의 모집 현황을 전체 수정합니다. 모든 필드를 포함해야 합니다.",
        request_body=recruitment_status_request,
        responses={
            200: openapi.Response('수정 성공', recruitment_status_response),
            400: openapi.Response('잘못된 요청', error_response),
            401: openapi.Response('인증 필요'),
            404: openapi.Response('연구실을 찾을 수 없음', error_response),
        }
    )
    def update(self, request, *args, **kwargs):
        """Update recruitment status"""
        # Clear cache when updating
        lab_id = kwargs.get('lab_id')
        if lab_id:
            CacheManager.invalidate_lab_caches(lab_id)

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="모집 현황 부분 수정",
        operation_description="연구실의 모집 현황을 부분 수정합니다. 수정할 필드만 포함하면 됩니다.",
        request_body=recruitment_status_request,
        responses={
            200: openapi.Response('수정 성공', recruitment_status_response),
            400: openapi.Response('잘못된 요청', error_response),
            401: openapi.Response('인증 필요'),
            404: openapi.Response('연구실을 찾을 수 없음', error_response),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update recruitment status"""
        # Clear cache when updating
        lab_id = kwargs.get('lab_id')
        if lab_id:
            CacheManager.invalidate_lab_caches(lab_id)

        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="모집 현황 삭제",
        operation_description="연구실의 모집 현황을 삭제합니다.",
        responses={
            204: openapi.Response('삭제 성공'),
            401: openapi.Response('인증 필요'),
            404: openapi.Response('연구실을 찾을 수 없음', error_response),
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete recruitment status"""
        # Clear cache when deleting
        lab_id = kwargs.get('lab_id')
        if lab_id:
            CacheManager.invalidate_lab_caches(lab_id)

        return super().destroy(request, *args, **kwargs)
