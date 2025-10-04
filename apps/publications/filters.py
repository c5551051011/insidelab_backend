# apps/publications/filters.py
import django_filters
from django.db.models import Q
from .models import Publication, Author, Venue


class PublicationFilter(django_filters.FilterSet):
    """논문 필터"""

    # 연도 범위 필터
    year_from = django_filters.NumberFilter(field_name='publication_year', lookup_expr='gte')
    year_to = django_filters.NumberFilter(field_name='publication_year', lookup_expr='lte')

    # 인용수 범위 필터
    min_citations = django_filters.NumberFilter(field_name='citation_count', lookup_expr='gte')
    max_citations = django_filters.NumberFilter(field_name='citation_count', lookup_expr='lte')

    # 학회/저널 필터
    venue = django_filters.NumberFilter(field_name='venues')
    venue_tier = django_filters.ChoiceFilter(
        field_name='venues__tier',
        choices=Venue.TIER_CHOICES
    )
    venue_type = django_filters.ChoiceFilter(
        field_name='venues__type',
        choices=Venue.TYPE_CHOICES
    )

    # 저자 필터
    author = django_filters.NumberFilter(field_name='authors')
    first_author = django_filters.NumberFilter(method='filter_first_author')

    # 연구실 필터
    lab = django_filters.NumberFilter(field_name='labs')
    lab_id = django_filters.NumberFilter(field_name='labs')  # lab_id로도 검색 가능

    # 연구 분야 필터 (이름으로 검색)
    research_area = django_filters.CharFilter(method='filter_by_research_area')
    research_area_id = django_filters.NumberFilter(field_name='research_areas')  # ID로 검색할 때 사용

    # 오픈 액세스 필터
    open_access = django_filters.BooleanFilter(field_name='is_open_access')

    # 수상 논문 필터
    award_paper = django_filters.BooleanFilter(method='filter_award_papers')

    # 최근 논문 필터
    recent_years = django_filters.NumberFilter(method='filter_recent_papers')

    # 고인용 논문 필터
    highly_cited = django_filters.BooleanFilter(method='filter_highly_cited')

    # 키워드 필터
    keyword = django_filters.CharFilter(method='filter_by_keyword')
    keywords_contain = django_filters.CharFilter(method='filter_keywords_contain')

    # 년도 구간 필터 (편의성 향상)
    year_range = django_filters.CharFilter(method='filter_year_range')

    # 특정 년도들 필터
    years = django_filters.CharFilter(method='filter_specific_years')

    # 추가 노트가 있는 논문 (수상 등)
    has_notes = django_filters.BooleanFilter(method='filter_has_notes')

    class Meta:
        model = Publication
        fields = [
            'publication_year', 'language', 'is_open_access'
        ]

    def filter_first_author(self, queryset, name, value):
        """첫 번째 저자로 필터링"""
        return queryset.filter(
            publicationauthor__author=value,
            publicationauthor__is_first_author=True
        )

    def filter_award_papers(self, queryset, name, value):
        """수상 논문 필터링"""
        if value:
            return queryset.filter(
                Q(publicationvenue__is_best_paper=True) |
                Q(publicationvenue__is_best_student_paper=True) |
                Q(publicationvenue__is_outstanding_paper=True)
            )
        return queryset

    def filter_recent_papers(self, queryset, name, value):
        """최근 N년간 논문 필터링"""
        from datetime import datetime
        if value:
            current_year = datetime.now().year
            return queryset.filter(publication_year__gte=current_year - value)
        return queryset

    def filter_highly_cited(self, queryset, name, value):
        """고인용 논문 필터링 (상위 10% 기준)"""
        if value:
            from django.db.models import Q
            # 간단히 인용수 50 이상으로 설정
            return queryset.filter(citation_count__gte=50)
        return queryset

    def filter_by_keyword(self, queryset, name, value):
        """특정 키워드로 필터링"""
        if value:
            return queryset.filter(keywords__icontains=value)
        return queryset

    def filter_keywords_contain(self, queryset, name, value):
        """키워드 배열에서 특정 문자열 포함 검색"""
        if value:
            keywords = [k.strip() for k in value.split(',')]
            q_objects = Q()
            for keyword in keywords:
                if keyword:
                    q_objects |= Q(keywords__icontains=keyword)
            return queryset.filter(q_objects)
        return queryset

    def filter_year_range(self, queryset, name, value):
        """년도 범위 필터 (예: '2020-2023')"""
        if value and '-' in value:
            try:
                start_year, end_year = value.split('-')
                start_year = int(start_year.strip())
                end_year = int(end_year.strip())
                return queryset.filter(
                    publication_year__gte=start_year,
                    publication_year__lte=end_year
                )
            except (ValueError, AttributeError):
                pass
        return queryset

    def filter_specific_years(self, queryset, name, value):
        """특정 년도들로 필터링 (예: '2020,2021,2023')"""
        if value:
            try:
                years = [int(year.strip()) for year in value.split(',')]
                return queryset.filter(publication_year__in=years)
            except (ValueError, AttributeError):
                pass
        return queryset

    def filter_has_notes(self, queryset, name, value):
        """추가 노트가 있는 논문 필터링"""
        if value:
            return queryset.exclude(additional_notes='')
        elif value is False:
            return queryset.filter(additional_notes='')
        return queryset

    def filter_by_research_area(self, queryset, name, value):
        """연구 분야 이름으로 필터링"""
        if value:
            return queryset.filter(research_areas__name__icontains=value)
        return queryset


class AuthorFilter(django_filters.FilterSet):
    """저자 필터"""

    # 인용수 범위 필터
    min_citations = django_filters.NumberFilter(field_name='total_citations', lookup_expr='gte')
    max_citations = django_filters.NumberFilter(field_name='total_citations', lookup_expr='lte')

    # H-index 범위 필터
    min_h_index = django_filters.NumberFilter(field_name='h_index', lookup_expr='gte')
    max_h_index = django_filters.NumberFilter(field_name='h_index', lookup_expr='lte')

    # 소속 필터
    affiliation = django_filters.CharFilter(
        field_name='current_affiliation',
        lookup_expr='icontains'
    )

    # 직책 필터
    position = django_filters.CharFilter(
        field_name='current_position',
        lookup_expr='icontains'
    )

    # 연구실 필터 (논문을 통한 연결)
    lab = django_filters.NumberFilter(method='filter_by_lab')

    # 논문 수 범위 필터
    min_publications = django_filters.NumberFilter(method='filter_min_publications')

    # 최근 활동 필터
    recent_activity = django_filters.BooleanFilter(method='filter_recent_activity')

    class Meta:
        model = Author
        fields = ['current_affiliation', 'current_position']

    def filter_min_publications(self, queryset, name, value):
        """최소 논문 수로 필터링"""
        if value:
            from django.db.models import Count
            return queryset.annotate(
                pub_count=Count('publications')
            ).filter(pub_count__gte=value)
        return queryset

    def filter_by_lab(self, queryset, name, value):
        """연구실로 필터링"""
        if value:
            return queryset.filter(publications__labs=value).distinct()
        return queryset

    def filter_recent_activity(self, queryset, name, value):
        """최근 3년간 활동한 저자 필터링"""
        if value:
            from datetime import datetime
            current_year = datetime.now().year
            return queryset.filter(
                publications__publication_year__gte=current_year - 3
            ).distinct()
        return queryset


class VenueFilter(django_filters.FilterSet):
    """학회/저널 필터"""

    # 타입 필터
    type = django_filters.ChoiceFilter(choices=Venue.TYPE_CHOICES)

    # 티어 필터
    tier = django_filters.ChoiceFilter(choices=Venue.TIER_CHOICES)

    # CORE 랭킹 필터
    core_ranking = django_filters.ChoiceFilter(choices=Venue.CORE_RANKING_CHOICES)

    # 분야 필터
    field = django_filters.CharFilter(lookup_expr='icontains')
    subfield = django_filters.CharFilter(lookup_expr='icontains')

    # H5-index 범위 필터
    min_h5_index = django_filters.NumberFilter(field_name='h5_index', lookup_expr='gte')
    max_h5_index = django_filters.NumberFilter(field_name='h5_index', lookup_expr='lte')

    # Impact Factor 범위 필터
    min_impact_factor = django_filters.NumberFilter(field_name='impact_factor', lookup_expr='gte')
    max_impact_factor = django_filters.NumberFilter(field_name='impact_factor', lookup_expr='lte')

    # 논문 수 필터
    min_publications = django_filters.NumberFilter(method='filter_min_publications')

    # 연구실 필터
    lab = django_filters.NumberFilter(method='filter_by_lab')

    class Meta:
        model = Venue
        fields = ['type', 'tier', 'core_ranking', 'field', 'subfield']

    def filter_min_publications(self, queryset, name, value):
        """최소 논문 수로 필터링"""
        if value:
            from django.db.models import Count
            return queryset.annotate(
                pub_count=Count('publications')
            ).filter(pub_count__gte=value)
        return queryset

    def filter_by_lab(self, queryset, name, value):
        """연구실로 필터링"""
        if value:
            return queryset.filter(publications__labs=value).distinct()
        return queryset