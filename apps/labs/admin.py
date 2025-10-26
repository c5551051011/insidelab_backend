
# apps/labs/admin.py
from django.contrib import admin
from .models import Lab, ResearchTopic, Publication, RecruitmentStatus

class ResearchTopicInline(admin.TabularInline):
    model = ResearchTopic
    extra = 1

class PublicationInline(admin.TabularInline):
    model = Publication
    extra = 1

class RecruitmentStatusInline(admin.StackedInline):
    model = RecruitmentStatus
    max_num = 1

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_professor', 'university', 'overall_rating', 'review_count']
    list_filter = ['university', 'department', 'overall_rating']
    search_fields = ['name', 'head_professor__name', 'university__name']
    readonly_fields = ['overall_rating', 'review_count', 'created_at', 'updated_at']
    inlines = [RecruitmentStatusInline, ResearchTopicInline, PublicationInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'head_professor', 'university_department', 'research_group')
        }),
        ('Details', {
            'fields': ('description', 'website', 'lab_size', 'research_areas', 'tags')
        }),
        ('Metrics', {
            'fields': ('overall_rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

