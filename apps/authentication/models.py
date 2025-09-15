# apps/authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    university = models.ForeignKey(
        'universities.University', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    position = models.CharField(
        max_length=50,
        choices=[
            ('PhD Student', 'PhD Student'),
            ('MS Student', 'MS Student'),
            ('Undergrad', 'Undergraduate Student'),
            ('PostDoc', 'PostDoc'),
            ('Research Assistant', 'Research Assistant'),
            ('faculty', 'Faculty'),
        ],
        blank=True
    )
    department = models.CharField(max_length=200, blank=True)
    lab_name = models.CharField(max_length=300, blank=True)
    
    # Verification and status
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('unverified', 'Unverified'),
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='unverified'
    )
    verification_token = models.CharField(max_length=100, blank=True)
    
    # Service provider capabilities
    is_lab_member = models.BooleanField(default=False)
    can_provide_services = models.BooleanField(default=False)
    
    # User activity stats
    review_count = models.IntegerField(default=0)
    helpful_votes = models.IntegerField(default=0)
    
    joined_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email
    
    @property
    def display_name(self):
        return self.name or self.email.split('@')[0]
    
    @property
    def verification_badge(self):
        if self.is_verified:
            return f"✓ {self.university.name}" if self.university else "✓ Verified"
        return "Unverified"


