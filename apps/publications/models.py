# apps/publications/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
import json


class ResearchArea(models.Model):
    """연구 분야 (계층적 구조)"""
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#3498db')  # hex color

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'research_areas'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        """상위 카테고리 포함한 전체 경로"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Venue(models.Model):
    """학회/저널 정보"""

    TYPE_CHOICES = [
        ('conference', 'Conference'),
        ('journal', 'Journal'),
        ('workshop', 'Workshop'),
        ('preprint', 'Preprint'),
    ]

    TIER_CHOICES = [
        ('top', 'Top Tier'),
        ('good', 'Good'),
        ('regular', 'Regular'),
        ('unknown', 'Unknown'),
    ]

    CORE_RANKING_CHOICES = [
        ('A*', 'A*'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]

    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # 등급/순위 정보
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='unknown')
    core_ranking = models.CharField(max_length=2, choices=CORE_RANKING_CHOICES, blank=True)
    h5_index = models.PositiveIntegerField(null=True, blank=True)
    h5_median = models.PositiveIntegerField(null=True, blank=True)
    impact_factor = models.FloatField(null=True, blank=True)

    # 분야 정보
    field = models.CharField(max_length=100, blank=True)
    subfield = models.CharField(max_length=100, blank=True)

    # 메타데이터
    website_url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'venues'
        unique_together = ['name', 'type']
        ordering = ['-tier', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    @property
    def display_name(self):
        return self.short_name or self.name


class Author(models.Model):
    """저자 정보"""
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)

    # 식별자들
    google_scholar_id = models.CharField(max_length=100, blank=True)
    orcid = models.CharField(max_length=50, blank=True, null=True, unique=True)
    dblp_id = models.CharField(max_length=255, blank=True)

    # 소속 정보 (현재)
    current_affiliation = models.CharField(max_length=255, blank=True)
    current_position = models.CharField(max_length=100, blank=True)

    # 메트릭스
    total_citations = models.PositiveIntegerField(default=0)
    h_index = models.PositiveIntegerField(default=0)
    i10_index = models.PositiveIntegerField(default=0)

    # 프로필 정보
    bio = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authors'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['google_scholar_id']),
        ]

    def __str__(self):
        return self.name


class Publication(models.Model):
    """논문 기본 정보"""
    title = models.TextField()
    abstract = models.TextField(blank=True)
    publication_year = models.PositiveIntegerField()
    publication_date = models.DateField(null=True, blank=True)
    doi = models.CharField(max_length=255, blank=True, null=True, unique=True)
    arxiv_id = models.CharField(max_length=50, blank=True)
    google_scholar_id = models.CharField(max_length=100, blank=True)

    # 메트릭스
    citation_count = models.PositiveIntegerField(default=0)
    h_index_contribution = models.FloatField(default=0.0)

    # 링크들
    paper_url = models.URLField(blank=True)
    code_url = models.URLField(blank=True)
    dataset_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    slides_url = models.URLField(blank=True)

    # 기타 정보
    page_count = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=10, default='en')
    is_open_access = models.BooleanField(default=False)

    # 키워드 및 추가 정보
    keywords = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="논문 키워드 목록"
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="추가 설명 (예: Best Paper Award, 특별한 성과 등)"
    )

    # 관계
    authors = models.ManyToManyField(Author, through='PublicationAuthor', related_name='publications')
    venues = models.ManyToManyField(Venue, through='PublicationVenue', related_name='publications')
    research_areas = models.ManyToManyField(ResearchArea, through='PublicationResearchArea', related_name='publications')
    labs = models.ManyToManyField('labs.Lab', related_name='publications', blank=True)

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'publications'
        ordering = ['-publication_year', '-citation_count']
        indexes = [
            models.Index(fields=['publication_year']),
            models.Index(fields=['citation_count']),
            models.Index(fields=['doi']),
        ]

    def __str__(self):
        return f"{self.title[:100]}... ({self.publication_year})"

    @property
    def first_author(self):
        """첫 번째 저자"""
        first_author_rel = self.publicationauthor_set.filter(is_first_author=True).first()
        return first_author_rel.author if first_author_rel else None

    @property
    def corresponding_author(self):
        """교신저자"""
        corresponding_rel = self.publicationauthor_set.filter(is_corresponding=True).first()
        return corresponding_rel.author if corresponding_rel else None

    @property
    def primary_venue(self):
        """주 발표 학회/저널"""
        return self.venues.first()


class PublicationVenue(models.Model):
    """논문-학회 연결"""

    PRESENTATION_CHOICES = [
        ('oral', 'Oral Presentation'),
        ('poster', 'Poster'),
        ('spotlight', 'Spotlight'),
        ('workshop', 'Workshop'),
        ('demo', 'Demo'),
    ]

    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    # 발표 정보
    presentation_type = models.CharField(max_length=20, choices=PRESENTATION_CHOICES, default='poster')
    session_name = models.CharField(max_length=255, blank=True)

    # 수상 정보
    is_best_paper = models.BooleanField(default=False)
    is_best_student_paper = models.BooleanField(default=False)
    is_outstanding_paper = models.BooleanField(default=False)
    award_name = models.CharField(max_length=255, blank=True)

    # 페이지 정보
    page_start = models.PositiveIntegerField(null=True, blank=True)
    page_end = models.PositiveIntegerField(null=True, blank=True)
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'publication_venues'
        unique_together = ['publication', 'venue']

    def __str__(self):
        return f"{self.publication.title[:50]} @ {self.venue.name}"

    @property
    def has_award(self):
        return any([self.is_best_paper, self.is_best_student_paper, self.is_outstanding_paper])


class PublicationAuthor(models.Model):
    """논문-저자 연결"""
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    # 저자 순서 및 역할
    author_order = models.PositiveIntegerField()
    is_corresponding = models.BooleanField(default=False)
    is_first_author = models.BooleanField(default=False)
    is_last_author = models.BooleanField(default=False)

    # 소속 정보 (논문 발표 당시)
    affiliation = models.CharField(max_length=255, blank=True)
    affiliation_lab = models.ForeignKey('labs.Lab', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'publication_authors'
        unique_together = ['publication', 'author_order']
        ordering = ['author_order']
        indexes = [
            models.Index(fields=['is_corresponding']),
            models.Index(fields=['affiliation_lab']),
        ]

    def __str__(self):
        return f"{self.author.name} ({self.author_order}) - {self.publication.title[:50]}"


class PublicationResearchArea(models.Model):
    """논문-연구분야 연결"""
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    research_area = models.ForeignKey(ResearchArea, on_delete=models.CASCADE)
    relevance_score = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    class Meta:
        db_table = 'publication_research_areas'
        unique_together = ['publication', 'research_area']

    def __str__(self):
        return f"{self.publication.title[:50]} - {self.research_area.name}"


class CitationMetric(models.Model):
    """인용 메트릭 히스토리"""

    SOURCE_CHOICES = [
        ('google_scholar', 'Google Scholar'),
        ('semantic_scholar', 'Semantic Scholar'),
        ('crossref', 'CrossRef'),
        ('manual', 'Manual'),
    ]

    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='citation_metrics')

    # 메트릭 정보
    citation_count = models.PositiveIntegerField()
    yearly_citations = models.JSONField(default=dict)  # {"2020": 5, "2021": 12}

    # 데이터 소스
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)

    # 추가 메트릭
    influential_citation_count = models.PositiveIntegerField(default=0)

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'citation_metrics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['recorded_at']),
        ]

    def __str__(self):
        return f"{self.publication.title[:50]} - {self.citation_count} citations ({self.source})"


class Collaboration(models.Model):
    """공동연구 관계"""

    COLLABORATOR_TYPE_CHOICES = [
        ('lab', 'Lab'),
        ('institution', 'Institution'),
        ('company', 'Company'),
    ]

    lab = models.ForeignKey('labs.Lab', on_delete=models.CASCADE, related_name='collaborations')
    collaborator_type = models.CharField(max_length=20, choices=COLLABORATOR_TYPE_CHOICES)
    collaborator_name = models.CharField(max_length=255)
    collaborator_id = models.PositiveBigIntegerField(null=True, blank=True)

    # 협력 정보
    collaboration_count = models.PositiveIntegerField(default=1)
    first_collaboration_year = models.PositiveIntegerField(null=True, blank=True)
    last_collaboration_year = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collaborations'
        ordering = ['-collaboration_count']
        indexes = [
            models.Index(fields=['lab', 'collaborator_type']),
        ]

    def __str__(self):
        return f"{self.lab.name} <-> {self.collaborator_name} ({self.collaboration_count} papers)"


class LabPublicationStats(models.Model):
    """연구실 논문 통계 (집계 테이블)"""
    lab = models.OneToOneField('labs.Lab', on_delete=models.CASCADE, related_name='publication_stats')

    total_publications = models.PositiveIntegerField(default=0)
    total_citations = models.PositiveIntegerField(default=0)
    h_index = models.PositiveIntegerField(default=0)
    top_tier_count = models.PositiveIntegerField(default=0)
    avg_citations_per_paper = models.FloatField(default=0.0)
    publications_last_5_years = models.PositiveIntegerField(default=0)

    # 최고 성과
    most_cited_paper_id = models.ForeignKey(
        Publication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    best_venue_tier = models.CharField(max_length=10, blank=True)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lab_publication_stats'

    def __str__(self):
        return f"{self.lab.name} - {self.total_publications} papers, {self.total_citations} citations"