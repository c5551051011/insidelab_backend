
# apps/universities/admin.py
from django.contrib import admin
from .models import University, Professor, ResearchGroup, Department, UniversityDepartment

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'state', 'city', 'ranking']
    list_filter = ['country', 'state']
    search_fields = ['name', 'city']
    ordering = ['name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(UniversityDepartment)
class UniversityDepartmentAdmin(admin.ModelAdmin):
    list_display = ['university', 'department', 'display_name', 'head_name', 'is_active']
    list_filter = ['university', 'department', 'is_active']
    search_fields = ['university__name', 'department__name', 'local_name']
    ordering = ['university__name', 'department__name']
    autocomplete_fields = ['university', 'department']

@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_department', 'get_university', 'head_professor']
    list_filter = ['university_department__university', 'university_department__department']
    search_fields = ['name', 'university_department__department__name', 'university_department__university__name']
    ordering = ['university_department__university__name', 'university_department__department__name', 'name']
    autocomplete_fields = ['university_department', 'head_professor']

    def get_department(self, obj):
        return obj.university_department.display_name
    get_department.short_description = 'Department'

    def get_university(self, obj):
        return obj.university_department.university.name
    get_university.short_description = 'University'

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_university', 'get_department', 'research_group', 'email']
    list_filter = ['university_department__university', 'university_department__department', 'research_group']
    search_fields = ['name', 'email']
    ordering = ['name']
    autocomplete_fields = ['university_department', 'research_group']

    def get_university(self, obj):
        return obj.university_department.university.name if obj.university_department else obj.university
    get_university.short_description = 'University'

    def get_department(self, obj):
        return obj.university_department.display_name if obj.university_department else obj.department
    get_department.short_description = 'Department'

