
# apps/universities/admin.py
from django.contrib import admin
from .models import University, Professor

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'state', 'city', 'ranking']
    list_filter = ['country', 'state']
    search_fields = ['name', 'city']
    ordering = ['name']

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'department', 'email']
    list_filter = ['university', 'department']
    search_fields = ['name', 'email']
    ordering = ['name']

