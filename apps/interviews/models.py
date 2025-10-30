# apps/sessions/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class ResearchArea(models.Model):
    """Research areas for interview matching"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'research_areas'
        ordering = ['name']

    def __str__(self):
        return self.name


class MockInterviewSession(models.Model):
    """Mock interview session booking model"""

    SESSION_TYPE_CHOICES = [
        ('mock_interview', 'Mock Interview'),
        ('qa_session', 'Q&A Session'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matching', 'Matching'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    MATCH_TYPE_CHOICES = [
        ('exact-lab', 'Exact Lab Match'),
        ('same-department', 'Same Department Match'),
        ('same-field', 'Same Field Match'),
    ]

    # User who booked the session
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='booked_sessions',
        help_text='User who booked this session'
    )

    # Session details
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default='mock_interview'
    )

    # Research area for matching
    research_area = models.ForeignKey(
        ResearchArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Primary research area for interviewer matching'
    )

    focus_areas = models.TextField(
        blank=True,
        help_text='Specific focus areas or topics to cover in the interview'
    )

    additional_notes = models.TextField(
        blank=True,
        help_text='Any additional notes or requests'
    )

    # Status and matching
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    match_type = models.CharField(
        max_length=20,
        choices=MATCH_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text='Type of match when interviewer is assigned'
    )

    # Interviewer (assigned later)
    interviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interview_sessions',
        help_text='Assigned interviewer'
    )

    # Confirmed schedule
    confirmed_date = models.DateField(
        null=True,
        blank=True,
        help_text='Confirmed session date'
    )

    confirmed_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Confirmed session time'
    )

    # Pricing
    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Total price in USD'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interview_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['interviewer', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_session_type_display()} - {self.user.email} ({self.status})"


class SessionLab(models.Model):
    """Target labs for session matching"""

    session = models.ForeignKey(
        MockInterviewSession,
        on_delete=models.CASCADE,
        related_name='target_labs'
    )

    lab = models.ForeignKey(
        'labs.Lab',
        on_delete=models.CASCADE,
        help_text='Target lab for matching'
    )

    priority = models.IntegerField(
        default=1,
        help_text='Priority order (1 = highest)'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'session_labs'
        ordering = ['priority']
        unique_together = ['session', 'lab']

    def __str__(self):
        return f"{self.session.id} - {self.lab.name} (Priority {self.priority})"


class SessionTimeSlot(models.Model):
    """Preferred time slots for session scheduling"""

    session = models.ForeignKey(
        MockInterviewSession,
        on_delete=models.CASCADE,
        related_name='preferred_slots'
    )

    date = models.DateField(help_text='Preferred date')
    time = models.TimeField(help_text='Preferred time')

    priority = models.IntegerField(
        default=1,
        help_text='Priority order (1 = first choice, 2 = second, 3 = third)'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'session_time_slots'
        ordering = ['priority']
        indexes = [
            models.Index(fields=['session', 'priority']),
        ]

    def __str__(self):
        return f"{self.session.id} - {self.date} {self.time} (Priority {self.priority})"
