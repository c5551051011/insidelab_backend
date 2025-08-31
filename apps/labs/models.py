
# apps/labs/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Lab(models.Model):
    name = models.CharField(max_length=300)
    professor = models.ForeignKey(
        'universities.Professor',
        on_delete=models.CASCADE,
        related_name='labs'
    )
    university = models.ForeignKey(
        'universities.University',
        on_delete=models.CASCADE,
        related_name='labs'
    )
    department = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    lab_size = models.IntegerField(null=True, blank=True)
    research_areas = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    
    # Calculated fields
    overall_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'labs'
        ordering = ['-overall_rating', '-review_count']

    def __str__(self):
        return f"{self.name} - {self.professor.name}"

    def update_rating(self):
        """Recalculate overall rating based on reviews"""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(lab=self)
        if reviews.exists():
            self.overall_rating = reviews.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating']
            self.review_count = reviews.count()
            self.save()


class ResearchTopic(models.Model):
    lab = models.ForeignKey(
        Lab, 
        on_delete=models.CASCADE, 
        related_name='research_topics'
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    keywords = models.JSONField(default=list)
    funding_info = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'research_topics'


class Publication(models.Model):
    lab = models.ForeignKey(
        Lab, 
        on_delete=models.CASCADE, 
        related_name='recent_publications'
    )
    title = models.CharField(max_length=500)
    authors = models.JSONField(default=list)
    venue = models.CharField(max_length=200)
    year = models.IntegerField()
    url = models.URLField(blank=True)
    abstract = models.TextField(blank=True)
    citations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'publications'
        ordering = ['-year', '-citations']


class RecruitmentStatus(models.Model):
    lab = models.OneToOneField(
        Lab,
        on_delete=models.CASCADE,
        related_name='recruitment_status'
    )
    is_recruiting_phd = models.BooleanField(default=False)
    is_recruiting_postdoc = models.BooleanField(default=False)
    is_recruiting_intern = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recruitment_status'
        verbose_name_plural = 'Recruitment statuses'

