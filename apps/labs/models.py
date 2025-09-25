
# apps/labs/models.py
from django.db import models
from django.db.models import Avg, Count
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
    research_group = models.ForeignKey(
        'universities.ResearchGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='labs',
        help_text='Optional research group this lab belongs to'
    )
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

    def save(self, *args, **kwargs):
        """Auto-populate research group from professor if not set"""
        if not self.research_group and self.professor and self.professor.research_group:
            self.research_group = self.professor.research_group

        # Ensure university and department consistency
        if self.professor:
            self.university = self.professor.university
            self.department = self.professor.department

        super().save(*args, **kwargs)

    def update_rating(self):
        """Recalculate overall rating based on reviews"""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(lab=self)
        if reviews.exists():
            self.overall_rating = reviews.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating']
            self.review_count = reviews.count()
            self.save(update_fields=['overall_rating', 'review_count'])


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


class LabCategoryAverage(models.Model):
    """Precomputed averages for each lab-category combination"""
    lab = models.ForeignKey(
        Lab,
        on_delete=models.CASCADE,
        related_name='category_averages'
    )
    category = models.ForeignKey(
        'reviews.RatingCategory',
        on_delete=models.CASCADE
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lab_category_averages'
        unique_together = ['lab', 'category']
        indexes = [
            models.Index(fields=['lab', 'category']),
            models.Index(fields=['category', 'average_rating']),
            models.Index(fields=['lab', 'average_rating']),
        ]
        ordering = ['lab', 'category__sort_order']

    def __str__(self):
        return f"{self.lab.name} - {self.category.display_name}: {self.average_rating}"

    @classmethod
    def update_lab_averages(cls, lab_id):
        """Update all category averages for a specific lab"""
        from apps.reviews.models import RatingCategory, ReviewRating

        try:
            lab = Lab.objects.get(id=lab_id)
            categories = RatingCategory.objects.filter(is_active=True)

            for category in categories:
                # Calculate average and count for this lab-category combination
                stats = ReviewRating.objects.filter(
                    review__lab=lab,
                    review__status='active',
                    category=category
                ).aggregate(
                    avg=Avg('rating'),
                    count=Count('rating')
                )

                avg_rating = stats['avg'] or 0.0
                review_count = stats['count'] or 0

                # Update or create the precomputed average
                cls.objects.update_or_create(
                    lab=lab,
                    category=category,
                    defaults={
                        'average_rating': avg_rating,
                        'review_count': review_count
                    }
                )

            # Also update the lab's overall rating
            lab.update_rating()

        except Lab.DoesNotExist:
            pass

    @classmethod
    def update_category_for_all_labs(cls, category_id):
        """Update a specific category average for all labs"""
        from apps.reviews.models import RatingCategory, ReviewRating

        try:
            category = RatingCategory.objects.get(id=category_id)
            labs = Lab.objects.all()

            for lab in labs:
                stats = ReviewRating.objects.filter(
                    review__lab=lab,
                    review__status='active',
                    category=category
                ).aggregate(
                    avg=Avg('rating'),
                    count=Count('rating')
                )

                avg_rating = stats['avg'] or 0.0
                review_count = stats['count'] or 0

                cls.objects.update_or_create(
                    lab=lab,
                    category=category,
                    defaults={
                        'average_rating': avg_rating,
                        'review_count': review_count
                    }
                )

        except RatingCategory.DoesNotExist:
            pass

    @classmethod
    def recalculate_all_averages(cls):
        """Recalculate all precomputed averages - useful for data migration"""
        labs = Lab.objects.all()
        for lab in labs:
            cls.update_lab_averages(lab.id)

