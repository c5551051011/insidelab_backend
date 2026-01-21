# apps/universities/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class University(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    ranking = models.IntegerField(null=True, blank=True)
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'universities'
        ordering = ['name']
        verbose_name_plural = 'Universities'

    def __str__(self):
        return self.name


class Department(models.Model):
    """Standard academic departments (e.g., Computer Science, Electrical Engineering)"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    common_names = models.JSONField(
        default=list,
        help_text="Alternative names for this department (e.g., 'CS', 'CompSci')"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class UniversityDepartment(models.Model):
    """Many-to-many relationship between universities and departments"""
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='university_departments'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='university_departments'
    )
    local_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="University-specific name if different from standard name"
    )
    website = models.URLField(blank=True)
    head_name = models.CharField(max_length=200, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'university_departments'
        unique_together = ['university', 'department']
        ordering = ['university__name', 'department__name']

    def __str__(self):
        if self.local_name:
            return f"{self.local_name} - {self.university.name}"
        return f"{self.department.name} - {self.university.name}"

    @property
    def display_name(self):
        return self.local_name or self.department.name


class ResearchGroup(models.Model):
    """Research groups within university departments (e.g., AI Lab, Systems Group)"""
    name = models.CharField(max_length=300)
    university_department = models.ForeignKey(
        UniversityDepartment,
        on_delete=models.CASCADE,
        related_name='research_groups',
        null=True,
        blank=True,
        help_text='The specific university-department combination this group belongs to'
    )
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    research_areas = models.JSONField(default=list)
    head_professor = models.ForeignKey(
        'Professor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'research_groups'
        ordering = ['university_department__university__name', 'university_department__department__name', 'name']
        unique_together = ['university_department', 'name']

    def __str__(self):
        return f"{self.name} - {self.university_department.display_name} - {self.university_department.university.name}"

    @property
    def university(self):
        return self.university_department.university

    @property
    def department(self):
        return self.university_department.department


class Professor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    university_department = models.ForeignKey(
        UniversityDepartment,
        on_delete=models.CASCADE,
        related_name='professors',
        null=True,
        blank=True,
        help_text='The specific university-department combination'
    )
    research_group = models.ForeignKey(
        ResearchGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='professors',
        help_text='Optional research group within the department'
    )
    lab = models.ForeignKey(
        'labs.Lab',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='professors',
        help_text='Lab this professor belongs to'
    )
    # Legacy fields for migration compatibility
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='legacy_professors',
        null=True,
        blank=True,
        help_text='Legacy field - use university_department instead'
    )
    department = models.CharField(max_length=200, blank=True, help_text='Legacy field - use university_department instead')
    profile_url = models.URLField(blank=True)
    google_scholar_url = models.URLField(blank=True)
    scholar_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Google Scholar author ID for scraping publications'
    )
    personal_website = models.URLField(blank=True)
    research_interests = models.JSONField(default=list)
    bio = models.TextField(blank=True)

    # Cached rating fields for performance
    overall_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Cached average rating from reviews'
    )
    review_count = models.IntegerField(
        default=0,
        help_text='Cached count of active reviews'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'professors'
        ordering = ['name']

    def __str__(self):
        if self.research_group:
            return f"{self.name} - {self.research_group.name} - {self.university.name}"
        return f"{self.name} - {self.department} - {self.university.name}"

    def update_rating(self):
        """Recalculate overall rating based on reviews"""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(professor=self, status='active')
        if reviews.exists():
            self.overall_rating = reviews.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating']
            self.review_count = reviews.count()
        else:
            self.overall_rating = 0
            self.review_count = 0
        self.save(update_fields=['overall_rating', 'review_count'])


class UniversityEmailDomain(models.Model):
    """University email domains for verification"""
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='email_domains'
    )
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Email domain (e.g., kaist.ac.kr, snu.ac.kr)"
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this domain has been verified as legitimate"
    )
    verification_type = models.CharField(
        max_length=20,
        choices=[
            ('official', 'Official University Domain'),
            ('student', 'Student Email Domain'),
            ('faculty', 'Faculty Email Domain'),
            ('staff', 'Staff Email Domain'),
            ('alumni', 'Alumni Email Domain'),
        ],
        default='official'
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this domain"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'university_email_domains'
        ordering = ['university__name', 'domain']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['university', 'is_active']),
        ]

    def __str__(self):
        return f"{self.university.name} - {self.domain}"

    @classmethod
    def is_university_email(cls, email):
        """Check if email domain belongs to a university"""
        if '@' not in email:
            return False

        domain = email.split('@')[1].lower()
        return cls.objects.filter(
            domain__iexact=domain,
            is_active=True,
            is_verified=True
        ).exists()

    @classmethod
    def get_university_by_email(cls, email):
        """Get university by email domain"""
        if '@' not in email:
            return None

        domain = email.split('@')[1].lower()
        try:
            domain_obj = cls.objects.get(
                domain__iexact=domain,
                is_active=True,
                is_verified=True
            )
            return domain_obj.university
        except cls.DoesNotExist:
            return None

