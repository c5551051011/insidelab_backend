# apps/publications/serializers.py
from rest_framework import serializers
from .models import (
    Publication, Author, Venue, ResearchArea,
    PublicationAuthor, PublicationVenue, PublicationResearchArea,
    CitationMetric, Collaboration, LabPublicationStats
)


class ResearchAreaSerializer(serializers.ModelSerializer):
    """연구 분야 시리얼라이저"""
    full_path = serializers.ReadOnlyField()
    children_count = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = ResearchArea
        fields = [
            'id', 'name', 'department', 'department_name', 'parent', 'description', 'color_code',
            'full_path', 'children_count', 'created_at'
        ]

    def get_children_count(self, obj):
        return obj.children.count()


class VenueSerializer(serializers.ModelSerializer):
    """학회/저널 시리얼라이저"""
    display_name = serializers.ReadOnlyField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    publication_count = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'short_name', 'type', 'type_display',
            'tier', 'tier_display', 'core_ranking',
            'h5_index', 'h5_median', 'impact_factor',
            'field', 'subfield', 'website_url', 'description',
            'display_name', 'publication_count',
            'created_at', 'updated_at'
        ]

    def get_publication_count(self, obj):
        return obj.publications.count()


class AuthorSerializer(serializers.ModelSerializer):
    """저자 시리얼라이저"""
    publication_count = serializers.SerializerMethodField()
    recent_publications = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'name', 'email', 'google_scholar_id', 'orcid', 'dblp_id',
            'current_affiliation', 'current_position',
            'total_citations', 'h_index', 'i10_index',
            'bio', 'profile_image_url', 'personal_website',
            'publication_count', 'recent_publications',
            'created_at', 'updated_at'
        ]

    def get_publication_count(self, obj):
        return obj.publications.count()

    def get_recent_publications(self, obj):
        from datetime import datetime
        current_year = datetime.now().year
        recent_pubs = obj.publications.filter(
            publication_year__gte=current_year - 3
        ).order_by('-publication_year')[:5]
        return PublicationListSerializer(recent_pubs, many=True).data


class PublicationAuthorSerializer(serializers.ModelSerializer):
    """논문-저자 관계 시리얼라이저"""
    author_name = serializers.CharField(source='author.name', read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    lab_name = serializers.CharField(source='affiliation_lab.name', read_only=True)

    class Meta:
        model = PublicationAuthor
        fields = [
            'author_id', 'author_name', 'author_order',
            'is_corresponding', 'is_first_author', 'is_last_author',
            'affiliation', 'affiliation_lab', 'lab_name'
        ]


class PublicationVenueSerializer(serializers.ModelSerializer):
    """논문-학회 관계 시리얼라이저"""
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    venue_type = serializers.CharField(source='venue.type', read_only=True)
    venue_tier = serializers.CharField(source='venue.tier', read_only=True)
    has_award = serializers.ReadOnlyField()

    class Meta:
        model = PublicationVenue
        fields = [
            'venue', 'venue_name', 'venue_type', 'venue_tier',
            'presentation_type', 'session_name',
            'is_best_paper', 'is_best_student_paper',
            'is_outstanding_paper', 'award_name', 'has_award',
            'page_start', 'page_end', 'volume', 'issue'
        ]


class PublicationMinimalSerializer(serializers.ModelSerializer):
    """논문 최소 필드 시리얼라이저 - Lab Detail용"""
    authors = serializers.SerializerMethodField()
    primary_venue_name = serializers.SerializerMethodField()
    primary_venue_tier = serializers.SerializerMethodField()
    research_area_names = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'publication_year',
            'doi', 'arxiv_id', 'google_scholar_id', 'citation_count',
            'authors', 'primary_venue_name', 'primary_venue_tier',
            'research_area_names', 'keywords', 'additional_notes',
            'paper_url', 'code_url', 'dataset_url', 'video_url', 'slides_url',
            'page_count', 'language', 'h_index_contribution'
        ]

    def to_representation(self, instance):
        """Always include all fields, even when empty"""
        data = super().to_representation(instance)

        # Ensure empty fields are included as empty strings instead of null
        string_fields = ['abstract', 'doi', 'arxiv_id', 'google_scholar_id',
                        'paper_url', 'code_url', 'dataset_url', 'video_url', 'slides_url',
                        'language', 'additional_notes']

        for field in string_fields:
            if data.get(field) is None:
                data[field] = ""

        # Ensure arrays are empty lists instead of null
        array_fields = ['keywords', 'research_area_names']
        for field in array_fields:
            if data.get(field) is None:
                data[field] = []

        # Ensure numeric fields have default values
        if data.get('page_count') is None:
            data['page_count'] = 0
        if data.get('h_index_contribution') is None:
            data['h_index_contribution'] = 0.0

        return data

    def get_authors(self, obj):
        """Get author names as simple list ordered by author_order"""
        authors_qs = obj.publicationauthor_set.select_related('author').order_by('author_order')
        return [pa.author.name for pa in authors_qs]

    def get_primary_venue_name(self, obj):
        venue = obj.primary_venue
        return venue.display_name if venue else ""

    def get_primary_venue_tier(self, obj):
        venue = obj.primary_venue
        return venue.tier if venue else ""

    def get_research_area_names(self, obj):
        return list(obj.research_areas.values_list('name', flat=True))


class PublicationListSerializer(serializers.ModelSerializer):
    """논문 목록용 간단한 시리얼라이저"""
    authors = serializers.SerializerMethodField()
    first_author_name = serializers.SerializerMethodField()
    primary_venue_name = serializers.SerializerMethodField()
    primary_venue_tier = serializers.SerializerMethodField()
    author_count = serializers.SerializerMethodField()
    research_area_names = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'publication_year', 'publication_date',
            'doi', 'arxiv_id', 'google_scholar_id', 'citation_count',
            'authors', 'first_author_name', 'author_count',
            'primary_venue_name', 'primary_venue_tier',
            'research_area_names', 'keywords', 'additional_notes',
            'paper_url', 'code_url', 'dataset_url', 'video_url', 'slides_url',
            'page_count', 'language', 'is_open_access',
            'h_index_contribution', 'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        """Always include all fields, even when empty"""
        data = super().to_representation(instance)

        # Ensure empty fields are included as empty strings instead of null
        string_fields = ['abstract', 'doi', 'arxiv_id', 'google_scholar_id',
                        'paper_url', 'code_url', 'dataset_url', 'video_url', 'slides_url',
                        'language', 'additional_notes']

        for field in string_fields:
            if data.get(field) is None:
                data[field] = ""

        # Ensure arrays are empty lists instead of null
        array_fields = ['keywords', 'research_area_names']
        for field in array_fields:
            if data.get(field) is None:
                data[field] = []

        # Ensure numeric fields have default values
        if data.get('page_count') is None:
            data['page_count'] = 0
        if data.get('h_index_contribution') is None:
            data['h_index_contribution'] = 0.0

        return data

    def get_authors(self, obj):
        """Get author names as simple list ordered by author_order"""
        authors_qs = obj.publicationauthor_set.select_related('author').order_by('author_order')
        return [pa.author.name for pa in authors_qs]

    def get_first_author_name(self, obj):
        first_author = obj.first_author
        return first_author.name if first_author else ""

    def get_primary_venue_name(self, obj):
        venue = obj.primary_venue
        return venue.display_name if venue else ""

    def get_primary_venue_tier(self, obj):
        venue = obj.primary_venue
        return venue.tier if venue else ""

    def get_author_count(self, obj):
        return obj.authors.count()

    def get_research_area_names(self, obj):
        return list(obj.research_areas.values_list('name', flat=True))


class PublicationDetailSerializer(serializers.ModelSerializer):
    """논문 상세 정보 시리얼라이저"""
    authors_detail = PublicationAuthorSerializer(
        source='publicationauthor_set',
        many=True,
        read_only=True
    )
    venues_detail = PublicationVenueSerializer(
        source='publicationvenue_set',
        many=True,
        read_only=True
    )
    research_areas_detail = ResearchAreaSerializer(
        source='research_areas',
        many=True,
        read_only=True
    )
    labs_detail = serializers.SerializerMethodField()
    citation_history = serializers.SerializerMethodField()

    first_author = serializers.SerializerMethodField()
    corresponding_author = serializers.SerializerMethodField()
    primary_venue = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'publication_year', 'publication_date',
            'doi', 'arxiv_id', 'google_scholar_id',
            'citation_count', 'h_index_contribution',
            'paper_url', 'code_url', 'dataset_url', 'video_url', 'slides_url',
            'page_count', 'language', 'is_open_access',
            'keywords', 'additional_notes',
            'authors_detail', 'venues_detail', 'research_areas_detail', 'labs_detail',
            'first_author', 'corresponding_author', 'primary_venue',
            'citation_history', 'created_at', 'updated_at'
        ]

    def get_first_author(self, obj):
        first_author = obj.first_author
        return AuthorSerializer(first_author).data if first_author else None

    def get_corresponding_author(self, obj):
        corresponding = obj.corresponding_author
        return AuthorSerializer(corresponding).data if corresponding else None

    def get_primary_venue(self, obj):
        venue = obj.primary_venue
        return VenueSerializer(venue).data if venue else None

    def get_labs_detail(self, obj):
        from apps.labs.serializers import LabListSerializer
        return LabListSerializer(obj.labs.all(), many=True).data

    def get_citation_history(self, obj):
        recent_metrics = obj.citation_metrics.order_by('-recorded_at')[:5]
        return CitationMetricSerializer(recent_metrics, many=True).data


class CitationMetricSerializer(serializers.ModelSerializer):
    """인용 메트릭 시리얼라이저"""
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = CitationMetric
        fields = [
            'id', 'citation_count', 'yearly_citations',
            'source', 'source_display', 'influential_citation_count',
            'recorded_at'
        ]


class CollaborationSerializer(serializers.ModelSerializer):
    """공동연구 시리얼라이저"""
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    collaborator_type_display = serializers.CharField(
        source='get_collaborator_type_display',
        read_only=True
    )
    collaboration_years = serializers.SerializerMethodField()

    class Meta:
        model = Collaboration
        fields = [
            'id', 'lab', 'lab_name',
            'collaborator_type', 'collaborator_type_display',
            'collaborator_name', 'collaborator_id',
            'collaboration_count', 'collaboration_years',
            'first_collaboration_year', 'last_collaboration_year',
            'created_at', 'updated_at'
        ]

    def get_collaboration_years(self, obj):
        if obj.first_collaboration_year and obj.last_collaboration_year:
            return obj.last_collaboration_year - obj.first_collaboration_year + 1
        return None


class LabPublicationStatsSerializer(serializers.ModelSerializer):
    """연구실 논문 통계 시리얼라이저"""
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    most_cited_paper_title = serializers.CharField(
        source='most_cited_paper.title',
        read_only=True
    )
    most_cited_paper_citations = serializers.IntegerField(
        source='most_cited_paper.citation_count',
        read_only=True
    )
    publications_by_year = serializers.SerializerMethodField()
    top_research_areas = serializers.SerializerMethodField()

    class Meta:
        model = LabPublicationStats
        fields = [
            'lab', 'lab_name',
            'total_publications', 'total_citations', 'h_index',
            'top_tier_count', 'avg_citations_per_paper',
            'publications_last_5_years', 'best_venue_tier',
            'most_cited_paper_id', 'most_cited_paper_title',
            'most_cited_paper_citations',
            'publications_by_year', 'top_research_areas',
            'last_updated'
        ]

    def get_publications_by_year(self, obj):
        from django.db.models import Count
        from datetime import datetime

        current_year = datetime.now().year
        years_data = obj.lab.publications.filter(
            publication_year__gte=current_year - 10
        ).values('publication_year').annotate(
            count=Count('id')
        ).order_by('publication_year')

        return {str(item['publication_year']): item['count'] for item in years_data}

    def get_top_research_areas(self, obj):
        from django.db.models import Count

        top_areas = ResearchArea.objects.filter(
            publications__labs=obj.lab
        ).annotate(
            pub_count=Count('publications')
        ).order_by('-pub_count')[:5]

        return [
            {
                'name': area.name,
                'publication_count': area.pub_count,
                'color_code': area.color_code
            }
            for area in top_areas
        ]