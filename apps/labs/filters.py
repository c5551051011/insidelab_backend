
# apps/labs/filters.py
import django_filters
from .models import Lab

class LabFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(field_name='overall_rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='overall_rating', lookup_expr='lte')
    university = django_filters.CharFilter(field_name='university_department__university__name', lookup_expr='icontains')
    university_id = django_filters.NumberFilter(field_name='university_department__university__id')
    university_department = django_filters.NumberFilter(field_name='university_department__id')
    head_professor = django_filters.NumberFilter(field_name='head_professor__id')
    research_group = django_filters.NumberFilter(field_name='research_group__id')
    research_area = django_filters.CharFilter(method='filter_research_area')
    tag = django_filters.CharFilter(method='filter_tag')
    recruiting_phd = django_filters.BooleanFilter(
        field_name='recruitment_status__is_recruiting_phd'
    )
    recruiting_postdoc = django_filters.BooleanFilter(
        field_name='recruitment_status__is_recruiting_postdoc'
    )
    recruiting_intern = django_filters.BooleanFilter(
        field_name='recruitment_status__is_recruiting_intern'
    )

    class Meta:
        model = Lab
        fields = ['department', 'min_rating', 'max_rating']

    def filter_research_area(self, queryset, name, value):
        return queryset.filter(research_areas__icontains=value)

    def filter_tag(self, queryset, name, value):
        return queryset.filter(tags__icontains=value)
