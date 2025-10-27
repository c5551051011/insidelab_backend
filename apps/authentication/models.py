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
    university_department = models.ForeignKey(
        'universities.UniversityDepartment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text='University department where the user belongs'
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
    # Legacy department field - will be populated from university_department for backward compatibility
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

    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    # University email verification
    university_email = models.EmailField(blank=True, null=True, help_text="University email for verification")
    university_email_verified = models.BooleanField(default=False)
    university_email_verification_token = models.CharField(max_length=100, blank=True)
    university_email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    verified_university = models.ForeignKey(
        'universities.University',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_users',
        help_text='University verified through email domain'
    )
    
    # Service provider capabilities
    is_lab_member = models.BooleanField(default=False)
    can_provide_services = models.BooleanField(default=False)
    
    # User activity stats
    review_count = models.IntegerField(default=0)
    helpful_votes = models.IntegerField(default=0)

    # Language preference
    language = models.CharField(
        max_length=10,
        choices=[
            ('ko', 'Korean'),
            ('en', 'English'),
        ],
        default='ko',
        help_text='User preferred language for emails and interface'
    )

    joined_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def save(self, *args, **kwargs):
        # Auto-populate legacy fields from university_department for backward compatibility
        if self.university_department:
            if not self.university:
                self.university = self.university_department.university
            if not self.department:
                self.department = self.university_department.department.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        return self.name or self.email.split('@')[0]

    @property
    def verification_badge(self):
        if self.is_verified:
            if self.university_department:
                return f"✓ {self.university_department.department.name} - {self.university_department.university.name}"
            elif self.university:
                return f"✓ {self.university.name}"
            else:
                return "✓ Verified"
        return "Unverified"


class UserLabInterest(models.Model):
    """Track labs that users are interested in"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lab_interests'
    )
    lab = models.ForeignKey(
        'labs.Lab',
        on_delete=models.CASCADE,
        related_name='interested_users'
    )
    interest_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General Interest'),
            ('application', 'Considering Application'),
            ('watching', 'Watching for Updates'),
            ('recruited', 'Applied/Recruited'),
        ],
        default='general'
    )
    notes = models.TextField(blank=True, help_text='Personal notes about interest in this lab')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_lab_interests'
        unique_together = ['user', 'lab']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.display_name} interested in {self.lab.name}"


class UserResearchProfile(models.Model):
    """User's research interests and specialties"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='research_profile'
    )
    primary_research_area = models.CharField(
        max_length=200,
        blank=True,
        help_text='Main research area (e.g., Machine Learning, Computer Vision)'
    )
    specialties_interests = models.JSONField(
        default=list,
        help_text='List of specific specialties and interests'
    )
    research_keywords = models.JSONField(
        default=list,
        help_text='Keywords related to research interests'
    )
    academic_background = models.TextField(
        blank=True,
        help_text='Brief academic background or experience'
    )
    research_goals = models.TextField(
        blank=True,
        help_text='Research goals or career objectives'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_research_profiles'

    def __str__(self):
        return f"Research profile for {self.user.display_name}"


