
# apps/universities/admin.py
from django.contrib import admin
from .models import University, Professor, ResearchGroup

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'state', 'city', 'ranking']
    list_filter = ['country', 'state']
    search_fields = ['name', 'city']
    ordering = ['name']

@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'university', 'head_professor']
    list_filter = ['university', 'department']
    search_fields = ['name', 'department', 'university__name']
    ordering = ['university__name', 'department', 'name']
    autocomplete_fields = ['university', 'head_professor']

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'department', 'research_group', 'email']
    list_filter = ['university', 'department', 'research_group']
    search_fields = ['name', 'email']
    ordering = ['name']
    autocomplete_fields = ['university', 'research_group']

