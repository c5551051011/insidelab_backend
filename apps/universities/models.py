# apps/universities/models.py
from django.db import models

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


class ResearchGroup(models.Model):
    """Research groups within university departments (e.g., AI Lab, Systems Group)"""
    name = models.CharField(max_length=300)
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='research_groups'
    )
    department = models.CharField(max_length=200)
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
        ordering = ['university__name', 'department', 'name']
        unique_together = ['university', 'department', 'name']

    def __str__(self):
        return f"{self.name} - {self.department} - {self.university.name}"


class Professor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='professors'
    )
    department = models.CharField(max_length=200)
    research_group = models.ForeignKey(
        ResearchGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='professors',
        help_text='Optional research group within the department'
    )
    profile_url = models.URLField(blank=True)
    google_scholar_url = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)
    research_interests = models.JSONField(default=list)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'professors'
        ordering = ['name']

    def __str__(self):
        if self.research_group:
            return f"{self.name} - {self.research_group.name} - {self.university.name}"
        return f"{self.name} - {self.department} - {self.university.name}"

