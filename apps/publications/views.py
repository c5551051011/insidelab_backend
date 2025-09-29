# apps/publications/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import Extract
from datetime import datetime, timedelta

from .models import (
    Publication, Author, Venue, ResearchArea,
    CitationMetric, Collaboration, LabPublicationStats
)
from .serializers import (
    PublicationListSerializer, PublicationDetailSerializer,
    AuthorSerializer, VenueSerializer, ResearchAreaSerializer,
    CitationMetricSerializer, CollaborationSerializer,
    LabPublicationStatsSerializer
)
from .filters import PublicationFilter, AuthorFilter, VenueFilter
from apps.utils.cache import cache_response


@method_decorator(cache_page(60 * 60), name='list')  # Cache list for 1 hour
@method_decorator(cache_page(60 * 60 * 2), name='retrieve')  # Cache detail for 2 hours
class PublicationViewSet(viewsets.ModelViewSet):
    """논문 관리 ViewSet"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PublicationFilter
    search_fields = ['title', 'abstract', 'authors__name', 'venues__name']
    ordering_fields = [
        'publication_year', 'citation_count', 'h_index_contribution',
        'created_at', 'title'
    ]
    ordering = ['-publication_year', '-citation_count']

    def get_queryset(self):
        queryset = Publication.objects.select_related().prefetch_related(
            'authors', 'venues', 'research_areas', 'labs',
            'publicationauthor_set__author',
            'publicationvenue_set__venue'
        )
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublicationDetailSerializer
        return PublicationListSerializer

    @cache_response('PUBLICATIONS', timeout=60*30)
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """최근 인기 논문 (최근 인용수 증가율 기준)"""
        current_year = datetime.now().year
        trending_papers = self.get_queryset().filter(
            publication_year__gte=current_year - 3,
            citation_count__gte=10
        )

        # Lab 필터링 추가
        lab_id = request.query_params.get('lab')
        if lab_id:
            trending_papers = trending_papers.filter(labs=lab_id)

        trending_papers = trending_papers.order_by('-citation_count', '-publication_year')[:20]

        serializer = self.get_serializer(trending_papers, many=True)
        return Response(serializer.data)

    @cache_response('PUBLICATIONS', timeout=60*60)
    @action(detail=False, methods=['get'])
    def top_cited(self, request):
        """가장 많이 인용된 논문들"""
        top_papers = self.get_queryset().filter(
            citation_count__gte=50
        )

        # Lab 필터링 추가
        lab_id = request.query_params.get('lab')
        if lab_id:
            top_papers = top_papers.filter(labs=lab_id)

        top_papers = top_papers.order_by('-citation_count')[:50]

        serializer = self.get_serializer(top_papers, many=True)
        return Response(serializer.data)

    @cache_response('PUBLICATIONS', timeout=60*15)
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """최근 발표된 논문들"""
        current_year = datetime.now().year
        recent_papers = self.get_queryset().filter(
            publication_year__gte=current_year - 1
        )

        # Lab 필터링 추가
        lab_id = request.query_params.get('lab')
        if lab_id:
            recent_papers = recent_papers.filter(labs=lab_id)

        recent_papers = recent_papers.order_by('-publication_year', '-created_at')[:30]

        serializer = self.get_serializer(recent_papers, many=True)
        return Response(serializer.data)

    @cache_response('PUBLICATIONS', timeout=60*60*2)
    @action(detail=False, methods=['get'])
    def by_lab(self, request):
        """연구실별 논문 분석"""
        lab_id = request.query_params.get('lab_id')
        if not lab_id:
            return Response(
                {'error': 'lab_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        publications = self.get_queryset().filter(labs=lab_id)

        # 기본 통계
        total_count = publications.count()
        total_citations = publications.aggregate(
            total=Sum('citation_count')
        )['total'] or 0

        # 연도별 통계
        yearly_stats = publications.values('publication_year').annotate(
            count=Count('id'),
            avg_citations=Avg('citation_count')
        ).order_by('-publication_year')[:10]

        # 탑 논문들
        top_papers = publications.order_by('-citation_count')[:10]
        top_papers_data = self.get_serializer(top_papers, many=True).data

        return Response({
            'lab_id': lab_id,
            'total_publications': total_count,
            'total_citations': total_citations,
            'avg_citations_per_paper': total_citations / total_count if total_count > 0 else 0,
            'yearly_statistics': list(yearly_stats),
            'top_publications': top_papers_data
        })

    @cache_response('PUBLICATIONS', timeout=60*60)
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """전체 논문 통계"""
        current_year = datetime.now().year

        # Lab 필터링 추가
        queryset = self.get_queryset()
        lab_id = request.query_params.get('lab')
        if lab_id:
            queryset = queryset.filter(labs=lab_id)

        # 기본 통계
        total_publications = queryset.count()
        total_citations = queryset.aggregate(
            total=Sum('citation_count')
        )['total'] or 0

        # 연도별 발표 논문 수
        yearly_publications = queryset.filter(
            publication_year__gte=current_year - 10
        ).values('publication_year').annotate(
            count=Count('id')
        ).order_by('publication_year')

        # 학회별 논문 수
        venue_stats = Venue.objects.annotate(
            publication_count=Count('publications')
        ).filter(publication_count__gt=0).order_by('-publication_count')[:10]

        # 연구 분야별 논문 수
        research_area_stats = ResearchArea.objects.annotate(
            publication_count=Count('publications')
        ).filter(publication_count__gt=0).order_by('-publication_count')[:10]

        return Response({
            'total_publications': total_publications,
            'total_citations': total_citations,
            'avg_citations_per_paper': total_citations / total_publications if total_publications > 0 else 0,
            'yearly_publications': [
                {'year': item['publication_year'], 'count': item['count']}
                for item in yearly_publications
            ],
            'top_venues': [
                {
                    'venue_name': venue.name,
                    'venue_tier': venue.tier,
                    'publication_count': venue.publication_count
                }
                for venue in venue_stats
            ],
            'top_research_areas': [
                {
                    'area_name': area.name,
                    'publication_count': area.publication_count,
                    'color_code': area.color_code
                }
                for area in research_area_stats
            ]
        })


@method_decorator(cache_page(60 * 60 * 6), name='list')  # Cache list for 6 hours
@method_decorator(cache_page(60 * 60 * 12), name='retrieve')  # Cache detail for 12 hours
class AuthorViewSet(viewsets.ModelViewSet):
    """저자 관리 ViewSet"""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuthorFilter
    search_fields = ['name', 'current_affiliation', 'bio']
    ordering_fields = ['name', 'total_citations', 'h_index', 'created_at']
    ordering = ['-total_citations', 'name']

    @cache_response('AUTHORS', timeout=60*60)
    @action(detail=False, methods=['get'])
    def top_cited(self, request):
        """가장 많이 인용된 저자들"""
        top_authors = self.get_queryset().filter(
            total_citations__gte=100
        )

        # Lab 필터링 추가
        lab_id = request.query_params.get('lab')
        if lab_id:
            top_authors = top_authors.filter(publications__labs=lab_id).distinct()

        top_authors = top_authors.order_by('-total_citations')[:20]

        serializer = self.get_serializer(top_authors, many=True)
        return Response(serializer.data)

    @cache_response('AUTHORS', timeout=60*30)
    @action(detail=True, methods=['get'])
    def publications(self, request, pk=None):
        """특정 저자의 논문들"""
        author = self.get_object()
        publications = author.publications.all().order_by('-publication_year')

        page = self.paginate_queryset(publications)
        if page is not None:
            serializer = PublicationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PublicationListSerializer(publications, many=True)
        return Response(serializer.data)

    @cache_response('AUTHORS', timeout=60*60)
    @action(detail=True, methods=['get'])
    def collaborators(self, request, pk=None):
        """공동 저자들"""
        author = self.get_object()

        # 같은 논문에 참여한 저자들
        collaborator_ids = author.publications.values_list(
            'authors', flat=True
        ).distinct().exclude(id=author.id)

        collaborators = Author.objects.filter(
            id__in=collaborator_ids
        ).annotate(
            collaboration_count=Count('publications', filter=Q(publications__authors=author))
        ).order_by('-collaboration_count')[:20]

        collaborator_data = []
        for collaborator in collaborators:
            collaborator_data.append({
                'author': AuthorSerializer(collaborator).data,
                'collaboration_count': collaborator.collaboration_count
            })

        return Response(collaborator_data)


@method_decorator(cache_page(60 * 60 * 12), name='list')  # Cache list for 12 hours
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')  # Cache detail for 24 hours
class VenueViewSet(viewsets.ModelViewSet):
    """학회/저널 관리 ViewSet"""
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VenueFilter
    search_fields = ['name', 'short_name', 'field', 'subfield']
    ordering_fields = ['name', 'tier', 'h5_index', 'impact_factor', 'created_at']
    ordering = ['-tier', 'name']

    @cache_response('VENUES', timeout=60*60*6)
    @action(detail=False, methods=['get'])
    def top_tier(self, request):
        """탑티어 학회/저널들"""
        top_venues = self.get_queryset().filter(
            tier='top'
        )

        # Lab 필터링 추가
        lab_id = request.query_params.get('lab')
        if lab_id:
            top_venues = top_venues.filter(publications__labs=lab_id).distinct()

        top_venues = top_venues.order_by('type', 'name')

        serializer = self.get_serializer(top_venues, many=True)
        return Response(serializer.data)

    @cache_response('VENUES', timeout=60*60*2)
    @action(detail=True, methods=['get'])
    def publications(self, request, pk=None):
        """특정 학회의 논문들"""
        venue = self.get_object()
        publications = venue.publications.all().order_by('-publication_year')

        page = self.paginate_queryset(publications)
        if page is not None:
            serializer = PublicationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PublicationListSerializer(publications, many=True)
        return Response(serializer.data)


@method_decorator(cache_page(60 * 60 * 12), name='list')  # Cache list for 12 hours
@method_decorator(cache_page(60 * 60 * 24), name='retrieve')  # Cache detail for 24 hours
class ResearchAreaViewSet(viewsets.ModelViewSet):
    """연구 분야 관리 ViewSet"""
    queryset = ResearchArea.objects.all()
    serializer_class = ResearchAreaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @cache_response('RESEARCH_AREAS', timeout=60*60*6)
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """계층적 연구 분야 구조"""
        root_areas = self.get_queryset().filter(parent__isnull=True)

        def build_tree(area):
            children = area.children.all()
            return {
                'id': area.id,
                'name': area.name,
                'description': area.description,
                'color_code': area.color_code,
                'publication_count': area.publications.count(),
                'children': [build_tree(child) for child in children]
            }

        hierarchy_data = [build_tree(area) for area in root_areas]
        return Response(hierarchy_data)

    @cache_response('RESEARCH_AREAS', timeout=60*60*2)
    @action(detail=True, methods=['get'])
    def publications(self, request, pk=None):
        """특정 연구 분야의 논문들"""
        area = self.get_object()
        publications = area.publications.all().order_by('-publication_year')

        page = self.paginate_queryset(publications)
        if page is not None:
            serializer = PublicationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PublicationListSerializer(publications, many=True)
        return Response(serializer.data)


@method_decorator(cache_page(60 * 60), name='list')  # Cache list for 1 hour
class LabPublicationStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """연구실 논문 통계 ViewSet"""
    queryset = LabPublicationStats.objects.select_related('lab', 'most_cited_paper')
    serializer_class = LabPublicationStatsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lab']
    ordering_fields = [
        'total_publications', 'total_citations', 'h_index',
        'avg_citations_per_paper', 'last_updated'
    ]
    ordering = ['-total_citations']

    @cache_response('LAB_STATS', timeout=60*60*2)
    @action(detail=False, methods=['get'])
    def rankings(self, request):
        """연구실 랭킹"""
        ranking_type = request.query_params.get('type', 'citations')

        if ranking_type == 'publications':
            stats = self.get_queryset().order_by('-total_publications')[:20]
        elif ranking_type == 'h_index':
            stats = self.get_queryset().order_by('-h_index')[:20]
        elif ranking_type == 'recent':
            stats = self.get_queryset().order_by('-publications_last_5_years')[:20]
        else:  # citations
            stats = self.get_queryset().order_by('-total_citations')[:20]

        serializer = self.get_serializer(stats, many=True)
        return Response({
            'ranking_type': ranking_type,
            'rankings': serializer.data
        })


@method_decorator(cache_page(60 * 30), name='list')  # Cache list for 30 minutes
class CollaborationViewSet(viewsets.ReadOnlyModelViewSet):
    """공동연구 관계 ViewSet"""
    queryset = Collaboration.objects.select_related('lab')
    serializer_class = CollaborationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lab', 'collaborator_type']
    ordering_fields = ['collaboration_count', 'last_collaboration_year']
    ordering = ['-collaboration_count']

    @cache_response('COLLABORATIONS', timeout=60*60)
    @action(detail=False, methods=['get'])
    def network(self, request):
        """공동연구 네트워크 분석"""
        min_collaborations = int(request.query_params.get('min_collaborations', 2))

        collaborations = self.get_queryset().filter(
            collaboration_count__gte=min_collaborations
        )

        # 네트워크 데이터 구성
        nodes = set()
        edges = []

        for collab in collaborations:
            lab_name = collab.lab.name
            collaborator_name = collab.collaborator_name

            nodes.add(lab_name)
            nodes.add(collaborator_name)

            edges.append({
                'source': lab_name,
                'target': collaborator_name,
                'weight': collab.collaboration_count,
                'type': collab.collaborator_type
            })

        return Response({
            'nodes': [{'id': node, 'name': node} for node in nodes],
            'edges': edges,
            'min_collaborations': min_collaborations
        })