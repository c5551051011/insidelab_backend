
# apps/reviews/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Review(models.Model):
    POSITION_CHOICES = [
        ('undergrad', 'Undergraduate'),
        ('ms', 'MS Student'),
        ('phd', 'PhD Student'),
        ('postdoc', 'Postdoc'),
        ('research_staff', 'Research Staff'),
        ('visiting', 'Visiting Researcher'),
    ]
    
    DURATION_CHOICES = [
        ('< 1 year', 'Less than 1 year'),
        ('1-2 years', '1-2 years'),
        ('2-3 years', '2-3 years'),
        ('3-4 years', '3-4 years'),
        ('4+ years', '4+ years'),
    ]
    
    lab = models.ForeignKey(
        'labs.Lab',
        on_delete=models.CASCADE,
        related_name='reviews'
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
    
    # Category ratings (stored as JSON)
    category_ratings = models.JSONField(default=dict)
    
    # Review content
    review_text = models.TextField()
    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)
    
    # Metadata
    is_verified = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-helpful_count', '-created_at']
        unique_together = ['lab', 'user']

    def __str__(self):
        return f"Review for {self.lab.name} by {self.user.email}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update lab rating after saving
        self.lab.update_rating()


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