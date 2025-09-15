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


class Professor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    university = models.ForeignKey(
        University, 
        on_delete=models.CASCADE, 
        related_name='professors'
    )
    department = models.CharField(max_length=200)
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
        return f"{self.name} - {self.university.name}"

