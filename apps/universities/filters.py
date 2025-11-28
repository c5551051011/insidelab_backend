# apps/universities/filters.py
import django_filters
from .models import Professor

class ProfessorFilter(django_filters.FilterSet):
    # Basic filters
    min_rating = django_filters.NumberFilter(field_name='overall_rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='overall_rating', lookup_expr='lte')
    min_reviews = django_filters.NumberFilter(field_name='review_count', lookup_expr='gte')

    # Single university/department filtering (existing)
    university = django_filters.NumberFilter(field_name='university__id')
    university_department = django_filters.NumberFilter(field_name='university_department__id')
    research_group = django_filters.NumberFilter(field_name='research_group__id')

    # Department ID filtering (directly by department, not university_department)
    department = django_filters.NumberFilter(field_name='university_department__department__id')

    # Multiple filtering support
    universities = django_filters.CharFilter(method='filter_universities')
    university_departments = django_filters.CharFilter(method='filter_university_departments')
    research_groups = django_filters.CharFilter(method='filter_research_groups')
    departments = django_filters.CharFilter(method='filter_departments')

    class Meta:
        model = Professor
        fields = ['name', 'overall_rating', 'review_count']

    def filter_universities(self, queryset, name, value):
        """Filter by multiple universities. Format: ?universities=1,2,3"""
        if value:
            university_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
            if university_ids:
                return queryset.filter(university__id__in=university_ids)
        return queryset

    def filter_university_departments(self, queryset, name, value):
        """Filter by multiple university departments. Format: ?university_departments=1,2,3"""
        if value:
            dept_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
            if dept_ids:
                return queryset.filter(university_department__id__in=dept_ids)
        return queryset

    def filter_research_groups(self, queryset, name, value):
        """Filter by multiple research groups. Format: ?research_groups=1,2,3"""
        if value:
            group_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
            if group_ids:
                return queryset.filter(research_group__id__in=group_ids)
        return queryset

    def filter_departments(self, queryset, name, value):
        """Filter by multiple departments. Format: ?departments=1,2,3"""
        if value:
            dept_ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
            if dept_ids:
                return queryset.filter(university_department__department__id__in=dept_ids)
        return queryset