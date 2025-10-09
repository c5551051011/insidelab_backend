# apps/publications/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count, Avg, Q, F, Sum
from django.db.models.functions import Extract
from datetime import datetime, timedelta

from .models import (
    Publication, Author, Venue, ResearchArea,
    CitationMetric, Collaboration, LabPublicationStats,
    PublicationAuthor, PublicationVenue, PublicationResearchArea
)
from .serializers import (
    PublicationMinimalSerializer, PublicationListSerializer, PublicationDetailSerializer,
    AuthorSerializer, VenueSerializer, ResearchAreaSerializer,
    CitationMetricSerializer, CollaborationSerializer,
    LabPublicationStatsSerializer
)
from .filters import PublicationFilter, AuthorFilter, VenueFilter
from apps.utils.cache import cache_response


# # @method_decorator(cache_page(60 * 60), name='list')  # Cache list for 1 hour
# @method_decorator(cache_page(60 * 60 * 2), name='retrieve')  # Cache detail for 2 hours
class PublicationViewSet(viewsets.ModelViewSet):
    """논문 관리 ViewSet"""
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PublicationFilter
    search_fields = ['title', 'abstract', 'authors__name', 'venues__name', 'keywords', 'additional_notes']
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

        # Check for fields parameter to determine serializer
        fields = self.request.query_params.get('fields', 'full')
        if fields == 'minimal':
            return PublicationMinimalSerializer
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

    @action(detail=False, methods=['get'])
    def yearly_stats(self, request):
        """특정 랩의 연도별 논문 개수 통계"""
        lab_id = request.query_params.get('lab_id')
        if not lab_id:
            return Response(
                {'error': 'lab_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 연도 범위 설정 (기본: 최근 10년)
        current_year = datetime.now().year
        start_year = int(request.query_params.get('start_year', current_year - 9))
        end_year = int(request.query_params.get('end_year', current_year))

        # 해당 랩의 논문들 필터링
        publications = self.get_queryset().filter(
            labs=lab_id,
            publication_year__gte=start_year,
            publication_year__lte=end_year
        )

        # 연도별 논문 개수 집계
        yearly_counts = publications.values('publication_year').annotate(
            count=Count('id')
        ).order_by('publication_year')

        # 결과를 딕셔너리 형태로 변환
        yearly_stats = {}
        for item in yearly_counts:
            year = str(item['publication_year'])
            yearly_stats[year] = item['count']

        # 빈 연도들도 0으로 채우기 (선택적)
        fill_empty_years = request.query_params.get('fill_empty', 'true').lower() == 'true'
        if fill_empty_years:
            for year in range(start_year, end_year + 1):
                year_str = str(year)
                if year_str not in yearly_stats:
                    yearly_stats[year_str] = 0

        return Response({
            'lab_id': lab_id,
            'yearly_stats': yearly_stats,
            'total_publications': sum(yearly_stats.values()),
            'year_range': {
                'start': start_year,
                'end': end_year
            }
        })

    @action(detail=False, methods=['get'])
    def filters(self, request):
        """특정 랩의 필터 옵션 제공 API"""
        lab_id = request.query_params.get('lab_id')
        if not lab_id:
            return Response(
                {'error': 'lab_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 해당 랩의 논문들 필터링
        publications = self.get_queryset().filter(labs=lab_id)

        # 1. 연도 옵션 (발표년도 기준)
        years = publications.values_list('publication_year', flat=True).distinct().order_by('-publication_year')
        years_list = [year for year in years if year]

        # 2. 학회/저널 옵션
        venues = publications.values(
            'venues__id', 'venues__name', 'venues__short_name', 'venues__type', 'venues__tier'
        ).distinct().order_by('venues__name')
        venues_list = []
        seen_venues = set()
        for venue in venues:
            if venue['venues__id'] and venue['venues__id'] not in seen_venues:
                venues_list.append({
                    'id': venue['venues__id'],
                    'name': venue['venues__name'],
                    'short_name': venue['venues__short_name'] or '',
                    'type': venue['venues__type'],
                    'tier': venue['venues__tier']
                })
                seen_venues.add(venue['venues__id'])

        # 3. 연구 분야 옵션
        research_areas = publications.values(
            'research_areas__id', 'research_areas__name'
        ).distinct().order_by('research_areas__name')
        research_areas_list = []
        seen_areas = set()
        for area in research_areas:
            if area['research_areas__id'] and area['research_areas__id'] not in seen_areas:
                research_areas_list.append({
                    'id': area['research_areas__id'],
                    'name': area['research_areas__name']
                })
                seen_areas.add(area['research_areas__id'])

        # 4. 학회 티어 옵션
        venue_tiers = publications.values_list('venues__tier', flat=True).distinct()
        tiers_list = [tier for tier in venue_tiers if tier and tier != 'unknown']

        # 5. 학회 타입 옵션
        venue_types = publications.values_list('venues__type', flat=True).distinct()
        types_list = [vtype for vtype in venue_types if vtype]

        return Response({
            'lab_id': lab_id,
            'filters': {
                'years': years_list,
                'venues': venues_list,
                'research_areas': research_areas_list,
                'venue_tiers': sorted(list(set(tiers_list))),
                'venue_types': sorted(list(set(types_list)))
            }
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """특정 랩의 요약/통계 API"""
        lab_id = request.query_params.get('lab_id')
        if not lab_id:
            return Response(
                {'error': 'lab_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 해당 랩의 논문들 필터링
        publications = self.get_queryset().filter(labs=lab_id)

        # 기본 통계
        total_publications = publications.count()
        total_citations = publications.aggregate(total=Sum('citation_count'))['total'] or 0
        avg_citations = total_citations / total_publications if total_publications > 0 else 0

        # 최근 5년 논문 수
        current_year = datetime.now().year
        recent_publications = publications.filter(
            publication_year__gte=current_year - 4
        ).count()

        # 탑 인용 논문
        top_cited_paper = publications.order_by('-citation_count').first()
        top_cited_info = None
        if top_cited_paper:
            top_cited_info = {
                'id': top_cited_paper.id,
                'title': top_cited_paper.title,
                'citation_count': top_cited_paper.citation_count,
                'publication_year': top_cited_paper.publication_year
            }

        # 주요 학회/저널 (논문 수 기준 상위 5개)
        top_venues = publications.values(
            'venues__name', 'venues__type', 'venues__tier'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # 주요 연구 분야 (논문 수 기준 상위 5개)
        top_research_areas = publications.values(
            'research_areas__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # 연도별 논문 수 (최근 10년)
        yearly_counts = publications.filter(
            publication_year__gte=current_year - 9
        ).values('publication_year').annotate(
            count=Count('id')
        ).order_by('publication_year')

        yearly_distribution = {}
        for item in yearly_counts:
            if item['publication_year']:
                yearly_distribution[str(item['publication_year'])] = item['count']

        # 오픈 액세스 논문 비율
        open_access_count = publications.filter(is_open_access=True).count()
        open_access_ratio = (open_access_count / total_publications * 100) if total_publications > 0 else 0

        # H-index 계산 (간단 버전)
        citations_list = list(publications.values_list('citation_count', flat=True).order_by('-citation_count'))
        h_index = 0
        for i, citations in enumerate(citations_list, 1):
            if citations >= i:
                h_index = i
            else:
                break

        return Response({
            'lab_id': lab_id,
            'summary': {
                'total_publications': total_publications,
                'total_citations': total_citations,
                'avg_citations_per_paper': round(avg_citations, 2),
                'recent_publications_5years': recent_publications,
                'h_index': h_index,
                'open_access_ratio': round(open_access_ratio, 1)
            },
            'top_cited_paper': top_cited_info,
            'top_venues': [
                {
                    'name': venue['venues__name'],
                    'type': venue['venues__type'],
                    'tier': venue['venues__tier'],
                    'publication_count': venue['count']
                }
                for venue in top_venues if venue['venues__name']
            ],
            'top_research_areas': [
                {
                    'name': area['research_areas__name'],
                    'publication_count': area['count']
                }
                for area in top_research_areas if area['research_areas__name']
            ],
            'yearly_distribution': yearly_distribution
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

    @cache_response('PUBLICATIONS', timeout=60*60)
    @action(detail=False, methods=['get'])
    def by_professor(self, request):
        """교수님별 논문 분석"""
        professor_id = request.query_params.get('professor_id')
        if not professor_id:
            return Response(
                {'error': 'professor_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 교수님의 논문들 (연구실을 통한 연결)
        publications = self.get_queryset().filter(
            Q(labs__professor_id=professor_id) |
            Q(authors__publications__labs__professor_id=professor_id)
        ).distinct()

        # 년도별 필터링
        year_from = request.query_params.get('year_from')
        year_to = request.query_params.get('year_to')
        if year_from:
            publications = publications.filter(publication_year__gte=int(year_from))
        if year_to:
            publications = publications.filter(publication_year__lte=int(year_to))

        # 키워드 필터링
        keywords = request.query_params.get('keywords')
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]
            q_objects = Q()
            for keyword in keyword_list:
                if keyword:
                    q_objects |= Q(keywords__icontains=keyword)
            publications = publications.filter(q_objects)

        # 기본 통계
        total_count = publications.count()
        total_citations = publications.aggregate(
            total=Sum('citation_count')
        )['total'] or 0

        # 연도별 통계
        yearly_stats = publications.values('publication_year').annotate(
            count=Count('id'),
            avg_citations=Avg('citation_count'),
            total_citations=Sum('citation_count')
        ).order_by('-publication_year')

        # 키워드별 통계
        all_keywords = []
        for pub in publications.values_list('keywords', flat=True):
            if pub:
                all_keywords.extend(pub)

        keyword_stats = {}
        for keyword in all_keywords:
            if keyword in keyword_stats:
                keyword_stats[keyword] += 1
            else:
                keyword_stats[keyword] = 1

        # 상위 키워드 10개
        top_keywords = sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:10]

        # 탑 논문들
        top_papers = publications.order_by('-citation_count')[:10]
        top_papers_data = self.get_serializer(top_papers, many=True).data

        # 수상 논문들
        award_papers = publications.exclude(additional_notes='').order_by('-publication_year')[:5]
        award_papers_data = self.get_serializer(award_papers, many=True).data

        return Response({
            'professor_id': professor_id,
            'total_publications': total_count,
            'total_citations': total_citations,
            'avg_citations_per_paper': total_citations / total_count if total_count > 0 else 0,
            'yearly_statistics': list(yearly_stats),
            'top_keywords': [{'keyword': k, 'count': v} for k, v in top_keywords],
            'top_publications': top_papers_data,
            'award_publications': award_papers_data
        })

    @cache_response('PUBLICATIONS', timeout=60*30)
    @action(detail=False, methods=['get'])
    def by_keywords(self, request):
        """키워드별 논문 검색 및 분석"""
        keywords = request.query_params.get('keywords')
        if not keywords:
            return Response(
                {'error': 'keywords parameter is required (comma-separated)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        keyword_list = [k.strip() for k in keywords.split(',')]
        q_objects = Q()
        for keyword in keyword_list:
            if keyword:
                q_objects |= Q(keywords__icontains=keyword)

        publications = self.get_queryset().filter(q_objects)

        # Lab 필터링
        lab_id = request.query_params.get('lab')
        if lab_id:
            publications = publications.filter(labs=lab_id)

        # 년도 필터링
        year_from = request.query_params.get('year_from')
        year_to = request.query_params.get('year_to')
        if year_from:
            publications = publications.filter(publication_year__gte=int(year_from))
        if year_to:
            publications = publications.filter(publication_year__lte=int(year_to))

        # 기본 통계
        total_count = publications.count()

        # 연도별 논문 수
        yearly_counts = publications.values('publication_year').annotate(
            count=Count('id')
        ).order_by('publication_year')

        # 연구실별 논문 수
        lab_counts = publications.values('labs__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # 페이지네이션 적용
        page = self.paginate_queryset(publications.order_by('-citation_count', '-publication_year'))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'statistics': {
                    'total_publications': total_count,
                    'searched_keywords': keyword_list,
                    'yearly_distribution': list(yearly_counts),
                    'top_labs': list(lab_counts)
                },
                'publications': serializer.data
            })

        serializer = self.get_serializer(publications, many=True)
        return Response({
            'statistics': {
                'total_publications': total_count,
                'searched_keywords': keyword_list,
                'yearly_distribution': list(yearly_counts),
                'top_labs': list(lab_counts)
            },
            'publications': serializer.data
        })

    @action(detail=False, methods=['post'])
    def create_with_relations(self, request):
        """논문과 모든 관련 데이터를 한번에 생성"""
        from django.db import transaction
        from apps.labs.models import Lab
        from apps.professors.models import Professor

        data = request.data

        # 필수 필드 검증
        required_fields = ['title', 'publication_year']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            with transaction.atomic():
                # 1. 논문 기본 정보 생성
                publication_data = {
                    'title': data['title'],
                    'publication_year': data['publication_year'],
                    'abstract': data.get('abstract', ''),
                    'doi': data.get('doi', ''),
                    'arxiv_id': data.get('arxiv_id', ''),
                    'citation_count': data.get('citation_count', 0),
                    'keywords': data.get('keywords', []),
                    'additional_notes': data.get('additional_notes', ''),
                    'paper_url': data.get('paper_url', ''),
                    'code_url': data.get('code_url', ''),
                    'video_url': data.get('video_url', ''),
                    'dataset_url': data.get('dataset_url', ''),
                    'slides_url': data.get('slides_url', ''),
                    'is_open_access': data.get('is_open_access', False),
                    'language': data.get('language', 'en'),
                    'page_count': data.get('page_count'),
                }

                if data.get('publication_date'):
                    from datetime import datetime
                    publication_data['publication_date'] = datetime.strptime(
                        data['publication_date'], '%Y-%m-%d'
                    ).date()

                publication = Publication.objects.create(**publication_data)

                # 2. 연구실 연결 (lab_id가 제공된 경우)
                lab_ids = data.get('lab_ids', [])
                if data.get('lab_id'):  # 단일 lab_id 지원
                    lab_ids.append(data['lab_id'])

                for lab_id in lab_ids:
                    try:
                        lab = Lab.objects.get(id=lab_id)
                        publication.labs.add(lab)
                    except Lab.DoesNotExist:
                        return Response(
                            {'error': f'Lab with id {lab_id} not found'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # 3. 저자 정보 처리
                authors_data = data.get('authors', [])
                for i, author_data in enumerate(authors_data):
                    # 기존 저자 찾기 또는 새로 생성
                    author_name = author_data.get('name')
                    author_email = author_data.get('email', '')

                    if not author_name:
                        continue

                    author, created = Author.objects.get_or_create(
                        name=author_name,
                        defaults={
                            'email': author_email,
                            'current_affiliation': author_data.get('affiliation', ''),
                            'current_position': author_data.get('position', ''),
                        }
                    )

                    # 논문-저자 관계 생성
                    PublicationAuthor.objects.create(
                        publication=publication,
                        author=author,
                        author_order=author_data.get('order', i + 1),
                        is_first_author=author_data.get('is_first_author', i == 0),
                        is_corresponding=author_data.get('is_corresponding', False),
                        is_last_author=author_data.get('is_last_author', False),
                        affiliation=author_data.get('affiliation', ''),
                        affiliation_lab_id=author_data.get('lab_id')
                    )

                # 4. 학회/저널 정보 처리
                venues_data = data.get('venues', [])
                for venue_data in venues_data:
                    venue_name = venue_data.get('name')
                    if not venue_name:
                        continue

                    venue, created = Venue.objects.get_or_create(
                        name=venue_name,
                        type=venue_data.get('type', 'conference'),
                        defaults={
                            'short_name': venue_data.get('short_name', ''),
                            'tier': venue_data.get('tier', 'unknown'),
                            'field': venue_data.get('field', ''),
                        }
                    )

                    # 논문-학회 관계 생성
                    PublicationVenue.objects.create(
                        publication=publication,
                        venue=venue,
                        presentation_type=venue_data.get('presentation_type', 'poster'),
                        is_best_paper=venue_data.get('is_best_paper', False),
                        is_best_student_paper=venue_data.get('is_best_student_paper', False),
                        is_outstanding_paper=venue_data.get('is_outstanding_paper', False),
                        award_name=venue_data.get('award_name', ''),
                    )

                # 5. 연구 분야 연결
                research_areas = data.get('research_areas', [])
                for area_name in research_areas:
                    area, created = ResearchArea.objects.get_or_create(
                        name=area_name,
                        defaults={'description': f'{area_name} 연구 분야'}
                    )
                    PublicationResearchArea.objects.create(
                        publication=publication,
                        research_area=area,
                        relevance_score=1.0
                    )

                # 6. 응답 데이터 생성
                serializer = PublicationDetailSerializer(publication)
                return Response({
                    'message': 'Publication created successfully with all relations',
                    'publication': serializer.data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Failed to create publication: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# @method_decorator(cache_page(60 * 60 * 6), name='list')  # Cache list for 6 hours
# @method_decorator(cache_page(60 * 60 * 12), name='retrieve')  # Cache detail for 12 hours
class AuthorViewSet(viewsets.ModelViewSet):
    """저자 관리 ViewSet"""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
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


# @method_decorator(cache_page(60 * 60 * 12), name='list')  # Cache list for 12 hours
# @method_decorator(cache_page(60 * 60 * 24), name='retrieve')  # Cache detail for 24 hours
class VenueViewSet(viewsets.ModelViewSet):
    """학회/저널 관리 ViewSet"""
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [AllowAny]
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


# @method_decorator(cache_page(60 * 60 * 12), name='list')  # Cache list for 12 hours
# @method_decorator(cache_page(60 * 60 * 24), name='retrieve')  # Cache detail for 24 hours
class ResearchAreaViewSet(viewsets.ModelViewSet):
    """연구 분야 관리 ViewSet"""
    queryset = ResearchArea.objects.all()
    serializer_class = ResearchAreaSerializer
    permission_classes = [AllowAny]
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


# @method_decorator(cache_page(60 * 60), name='list')  # Cache list for 1 hour
class LabPublicationStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """연구실 논문 통계 ViewSet"""
    queryset = LabPublicationStats.objects.select_related('lab', 'most_cited_paper')
    serializer_class = LabPublicationStatsSerializer
    permission_classes = [AllowAny]
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


# @method_decorator(cache_page(60 * 30), name='list')  # Cache list for 30 minutes
class CollaborationViewSet(viewsets.ReadOnlyModelViewSet):
    """공동연구 관계 ViewSet"""
    queryset = Collaboration.objects.select_related('lab')
    serializer_class = CollaborationSerializer
    permission_classes = [AllowAny]
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