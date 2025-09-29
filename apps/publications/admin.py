# apps/publications/admin.py
from django.contrib import admin
from django.db.models import Count
from .models import (
    Publication, Author, Venue, ResearchArea,
    PublicationAuthor, PublicationVenue, PublicationResearchArea,
    CitationMetric, Collaboration, LabPublicationStats
)


class PublicationAuthorInline(admin.TabularInline):
    model = PublicationAuthor
    extra = 0
    autocomplete_fields = ['author']


class PublicationVenueInline(admin.TabularInline):
    model = PublicationVenue
    extra = 0
    autocomplete_fields = ['venue']


class PublicationResearchAreaInline(admin.TabularInline):
    model = PublicationResearchArea
    extra = 0
    autocomplete_fields = ['research_area']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = [
        'title_short', 'publication_year', 'citation_count',
        'first_author_name', 'primary_venue_name', 'is_open_access'
    ]
    list_filter = [
        'publication_year', 'is_open_access', 'language',
        ('venues__tier', admin.ChoicesFieldListFilter),
        ('venues__type', admin.ChoicesFieldListFilter)
    ]
    search_fields = ['title', 'abstract', 'doi', 'authors__name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['labs']

    inlines = [PublicationAuthorInline, PublicationVenueInline, PublicationResearchAreaInline]

    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'abstract', 'publication_year', 'publication_date')
        }),
        ('식별자', {
            'fields': ('doi', 'arxiv_id', 'google_scholar_id'),
            'classes': ('collapse',)
        }),
        ('메트릭스', {
            'fields': ('citation_count', 'h_index_contribution')
        }),
        ('링크들', {
            'fields': ('paper_url', 'code_url', 'dataset_url', 'video_url', 'slides_url'),
            'classes': ('collapse',)
        }),
        ('기타 정보', {
            'fields': ('page_count', 'language', 'is_open_access', 'labs'),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def title_short(self, obj):
        return obj.title[:100] + '...' if len(obj.title) > 100 else obj.title
    title_short.short_description = 'Title'

    def first_author_name(self, obj):
        first_author = obj.first_author
        return first_author.name if first_author else '-'
    first_author_name.short_description = 'First Author'

    def primary_venue_name(self, obj):
        venue = obj.primary_venue
        return venue.display_name if venue else '-'
    primary_venue_name.short_description = 'Venue'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'authors', 'venues', 'publicationauthor_set__author'
        )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'current_affiliation', 'total_citations',
        'h_index', 'publication_count'
    ]
    list_filter = ['current_position', 'created_at']
    search_fields = ['name', 'email', 'current_affiliation', 'orcid']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'email')
        }),
        ('식별자', {
            'fields': ('google_scholar_id', 'orcid', 'dblp_id'),
            'classes': ('collapse',)
        }),
        ('현재 소속', {
            'fields': ('current_affiliation', 'current_position')
        }),
        ('메트릭스', {
            'fields': ('total_citations', 'h_index', 'i10_index')
        }),
        ('프로필', {
            'fields': ('bio', 'profile_image_url', 'personal_website'),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def publication_count(self, obj):
        return obj.publications.count()
    publication_count.short_description = 'Publications'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            pub_count=Count('publications')
        )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'short_name', 'type', 'tier',
        'core_ranking', 'field', 'publication_count'
    ]
    list_filter = ['type', 'tier', 'core_ranking', 'field']
    search_fields = ['name', 'short_name', 'field', 'subfield']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'short_name', 'type')
        }),
        ('등급/순위', {
            'fields': ('tier', 'core_ranking', 'h5_index', 'h5_median', 'impact_factor')
        }),
        ('분야', {
            'fields': ('field', 'subfield')
        }),
        ('메타데이터', {
            'fields': ('website_url', 'description'),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def publication_count(self, obj):
        return obj.publications.count()
    publication_count.short_description = 'Publications'


@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'publication_count', 'color_code']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    autocomplete_fields = ['parent']

    def publication_count(self, obj):
        return obj.publications.count()
    publication_count.short_description = 'Publications'


@admin.register(CitationMetric)
class CitationMetricAdmin(admin.ModelAdmin):
    list_display = [
        'publication_short', 'citation_count', 'source',
        'influential_citation_count', 'recorded_at'
    ]
    list_filter = ['source', 'recorded_at']
    search_fields = ['publication__title']
    readonly_fields = ['recorded_at']

    def publication_short(self, obj):
        return obj.publication.title[:50] + '...'
    publication_short.short_description = 'Publication'


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = [
        'lab', 'collaborator_name', 'collaborator_type',
        'collaboration_count', 'first_collaboration_year',
        'last_collaboration_year'
    ]
    list_filter = ['collaborator_type', 'first_collaboration_year']
    search_fields = ['lab__name', 'collaborator_name']
    autocomplete_fields = ['lab']


@admin.register(LabPublicationStats)
class LabPublicationStatsAdmin(admin.ModelAdmin):
    list_display = [
        'lab', 'total_publications', 'total_citations',
        'h_index', 'avg_citations_per_paper', 'last_updated'
    ]
    list_filter = ['best_venue_tier', 'last_updated']
    search_fields = ['lab__name']
    readonly_fields = ['last_updated']
    autocomplete_fields = ['lab', 'most_cited_paper_id']

    fieldsets = (
        ('기본 통계', {
            'fields': ('lab', 'total_publications', 'total_citations', 'h_index')
        }),
        ('세부 메트릭', {
            'fields': ('top_tier_count', 'avg_citations_per_paper', 'publications_last_5_years')
        }),
        ('최고 성과', {
            'fields': ('most_cited_paper_id', 'best_venue_tier')
        }),
        ('시스템 정보', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        })
    )


# Inline admin for related models
class PublicationInline(admin.TabularInline):
    model = Publication.labs.through
    extra = 0
    autocomplete_fields = ['publication']


# Add publications to Lab admin if it exists
try:
    from apps.labs.admin import LabAdmin
    LabAdmin.inlines = getattr(LabAdmin, 'inlines', []) + [PublicationInline]
except ImportError:
    pass