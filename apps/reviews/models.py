
# apps/reviews/models.py
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class RatingCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rating_categories'
        ordering = ['sort_order', 'display_name']
        verbose_name_plural = 'Rating Categories'

    def __str__(self):
        return self.display_name

class Review(models.Model):
    POSITION_CHOICES = [
        ('PhD Student', 'PhD Student'),
        ('MS Student', 'MS Student'),
        ('Undergrad', 'Undergraduate Student'),
        ('PostDoc', 'PostDoc'),
        ('Research Assistant', 'Research Assistant'),
    ]
    
    DURATION_CHOICES = [
        ('< 6 months', 'Less than 6 months'),
        ('6 months', '6 months'),
        ('1 year', '1 year'),
        ('2 years', '2 years'),
        ('3 years', '3 years'),
        ('4+ years', '4+ years'),
    ]
    
    professor = models.ForeignKey(
        'universities.Professor',
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
        help_text='Professor this review is about (required)'
    )
    lab = models.ForeignKey(
        'labs.Lab',
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
        help_text='Lab context for the review (optional)'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    duration = models.CharField(max_length=50, choices=DURATION_CHOICES)
    
    # Overall rating
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # Review content
    review_text = models.TextField()
    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)

    # Metadata
    is_verified = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        default='active',
        choices=[('active', 'Active'), ('deleted', 'Deleted'), ('flagged', 'Flagged')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-helpful_count', '-created_at']
        unique_together = ['professor', 'user']

    def __str__(self):
        lab_context = f" in {self.lab.name}" if self.lab else ""
        return f"Review for {self.professor.name}{lab_context} by {self.user.email}"

    @property
    def category_ratings_dict(self):
        """Return category ratings as a dictionary for API responses"""
        ratings = {}
        for rating in self.category_ratings.select_related('category').filter(category__is_active=True):
            ratings[rating.category.display_name] = float(rating.rating)
        return ratings

    def set_category_ratings(self, ratings_dict):
        """Set category ratings from a dictionary"""
        from apps.reviews.models import RatingCategory

        # Clear existing ratings for this review
        self.category_ratings.all().delete()

        # Create new ratings
        for category_name, rating_value in ratings_dict.items():
            try:
                category = RatingCategory.objects.get(
                    Q(display_name=category_name) | Q(name=category_name),
                    is_active=True
                )
                ReviewRating.objects.create(
                    review=self,
                    category=category,
                    rating=rating_value
                )
            except RatingCategory.DoesNotExist:
                continue

    @classmethod
    def get_active_categories(cls):
        """Get all active rating categories"""
        return RatingCategory.objects.filter(is_active=True).order_by('sort_order')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update precomputed averages after saving
        self.update_lab_averages()

    def delete(self, *args, **kwargs):
        lab_id = self.lab.id
        super().delete(*args, **kwargs)
        # Update precomputed averages after deletion
        self.update_lab_averages_by_id(lab_id)

    def update_lab_averages(self):
        """Update precomputed averages for this review's lab"""
        from apps.labs.models import LabCategoryAverage
        LabCategoryAverage.update_lab_averages(self.lab.id)

    @staticmethod
    def update_lab_averages_by_id(lab_id):
        """Update precomputed averages for a lab by ID"""
        from apps.labs.models import LabCategoryAverage
        LabCategoryAverage.update_lab_averages(lab_id)


class ReviewRating(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='category_ratings'
    )
    category = models.ForeignKey(
        RatingCategory,
        on_delete=models.CASCADE
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_ratings'
        unique_together = ['review', 'category']
        indexes = [
            models.Index(fields=['review', 'category']),
            models.Index(fields=['category', 'rating']),
        ]

    def __str__(self):
        return f"{self.review} - {self.category.display_name}: {self.rating}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update precomputed averages when rating changes
        self.update_lab_averages()

    def delete(self, *args, **kwargs):
        lab_id = self.review.lab.id
        super().delete(*args, **kwargs)
        # Update precomputed averages after deletion
        self.update_lab_averages_by_id(lab_id)

    def update_lab_averages(self):
        """Update precomputed averages for this rating's lab"""
        from apps.labs.models import LabCategoryAverage
        LabCategoryAverage.update_lab_averages(self.review.lab.id)

    @staticmethod
    def update_lab_averages_by_id(lab_id):
        """Update precomputed averages for a lab by ID"""
        from apps.labs.models import LabCategoryAverage
        LabCategoryAverage.update_lab_averages(lab_id)


class ReviewHelpful(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_helpful_votes'
        unique_together = ['review', 'user']