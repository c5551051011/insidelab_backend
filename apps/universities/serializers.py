
# apps/universities/serializers.py
from rest_framework import serializers
from django.db import models
from .models import University, Professor, ResearchGroup, UniversityDepartment, Department


class UniversityMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'city', 'country']


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class DepartmentMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class DepartmentSerializer(serializers.ModelSerializer):
    university_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'common_names', 'university_count', 'created_at']

    def get_university_count(self, obj):
        return obj.university_departments.filter(is_active=True).count()


class UniversityDepartmentMinimalSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='local_name', read_only=True)

    class Meta:
        model = UniversityDepartment
        fields = ['id', 'department', 'name']


class UniversityDepartmentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = UniversityDepartment
        fields = ['id', 'department', 'department_name', 'university', 'university_name',
                 'local_name', 'display_name', 'website', 'head_name', 'established_year',
                 'is_active', 'created_at']
        read_only_fields = ['display_name']
        extra_kwargs = {
            'university': {'required': False}
        }


class ResearchGroupMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchGroup
        fields = ['id', 'name']


class ResearchGroupSerializer(serializers.ModelSerializer):
    university_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    head_professor_name = serializers.SerializerMethodField()
    professor_count = serializers.SerializerMethodField()
    lab_count = serializers.SerializerMethodField()

    class Meta:
        model = ResearchGroup
        fields = [
            'id', 'name', 'university_department', 'university_name', 'department_name',
            'description', 'website', 'research_areas', 'head_professor',
            'head_professor_name', 'professor_count', 'lab_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'university_name', 'department_name', 'head_professor_name',
            'professor_count', 'lab_count', 'created_at', 'updated_at'
        ]

    def get_university_name(self, obj):
        return obj.university_department.university.name if obj.university_department else None

    def get_department_name(self, obj):
        return obj.university_department.department.name if obj.university_department else None

    def get_head_professor_name(self, obj):
        return obj.head_professor.name if obj.head_professor else None

    def get_professor_count(self, obj):
        return obj.professors.count()

    def get_lab_count(self, obj):
        return obj.labs.count()


class ProfessorMinimalSerializer(serializers.ModelSerializer):
    lab = serializers.SerializerMethodField()
    overall_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    research_areas = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    recruitment_status = serializers.SerializerMethodField()
    university_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)

    class Meta:
        model = Professor
        fields = [
            'id',
            'name',
            'email',
            'google_scholar_url',
            'lab',
            'overall_rating',
            'review_count',
            'research_areas',
            'tags',
            'recruitment_status',
            'university_name',
            'department_name',
            'research_group_name',
        ]

    def get_lab(self, obj):
        """Return lab this professor belongs to"""
        try:
            if obj.lab:
                return {
                    'id': obj.lab.id,
                    'name': obj.lab.name,
                    'website': obj.lab.website
                }

            # Fallback to headed_labs if professor is head of a lab
            if hasattr(obj, 'headed_labs') and obj.headed_labs.exists():
                lab = obj.headed_labs.first()
                return {
                    'id': lab.id,
                    'name': lab.name,
                    'website': lab.website
                }
        except Exception as e:
            # For debugging, you might want to log this error
            pass

        return None

    def get_overall_rating(self, obj):
        """Return cached overall rating"""
        return f"{obj.overall_rating:.2f}"

    def get_review_count(self, obj):
        """Return cached review count"""
        return obj.review_count

    def get_research_areas(self, obj):
        """Return research areas - using research_interests field"""
        return obj.research_interests or []

    def get_tags(self, obj):
        """Return tags from the professor's lab if they belong to one"""
        try:
            if obj.lab and hasattr(obj.lab, 'tags'):
                return obj.lab.tags or []
            # If professor heads a lab, use that lab's tags
            if obj.headed_labs.exists():
                lab = obj.headed_labs.first()
                return lab.tags or []
        except:
            pass
        return []

    def get_recruitment_status(self, obj):
        """Return recruitment status for this professor"""
        try:
            if hasattr(obj, 'recruitment_status'):
                recruitment = obj.recruitment_status
                return {
                    'is_recruiting_phd': recruitment.is_recruiting_phd,
                    'is_recruiting_postdoc': recruitment.is_recruiting_postdoc,
                    'is_recruiting_intern': recruitment.is_recruiting_intern,
                    'notes': recruitment.notes,
                    'last_updated': recruitment.last_updated
                }
        except:
            pass
        return None


class ProfessorSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)
    lab_info = serializers.SerializerMethodField()
    overall_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    research_areas = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    recruitment_status = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = '__all__'

    def get_lab_info(self, obj):
        """Return lab this professor belongs to"""
        if obj.lab:
            return {
                'id': obj.lab.id,
                'name': obj.lab.name,
                'website': obj.lab.website
            }

        # Fallback to headed_labs if professor is head of a lab
        try:
            if obj.headed_labs.exists():
                lab = obj.headed_labs.first()
                return {
                    'id': lab.id,
                    'name': lab.name,
                    'website': lab.website
                }
        except:
            pass

        return None

    def get_overall_rating(self, obj):
        """Return cached overall rating"""
        return f"{obj.overall_rating:.2f}"

    def get_review_count(self, obj):
        """Return cached review count"""
        return obj.review_count

    def get_research_areas(self, obj):
        """Return research areas - using research_interests field"""
        return obj.research_interests or []

    def get_tags(self, obj):
        """Return tags from the professor's lab if they belong to one"""
        try:
            if obj.lab and hasattr(obj.lab, 'tags'):
                return obj.lab.tags or []
            # If professor heads a lab, use that lab's tags
            if obj.headed_labs.exists():
                lab = obj.headed_labs.first()
                return lab.tags or []
        except:
            pass
        return []

    def get_recruitment_status(self, obj):
        """Return recruitment status from professor's lab if available"""
        try:
            # Check if professor has a lab and that lab has recruitment status
            if obj.lab and hasattr(obj.lab, 'recruitment_status'):
                recruitment = obj.lab.recruitment_status
                return {
                    'is_recruiting_phd': recruitment.is_recruiting_phd,
                    'is_recruiting_postdoc': recruitment.is_recruiting_postdoc,
                    'is_recruiting_intern': recruitment.is_recruiting_intern,
                    'notes': recruitment.notes,
                    'last_updated': recruitment.last_updated
                }
            # If professor heads a lab, use that lab's recruitment status
            if obj.headed_labs.exists():
                lab = obj.headed_labs.first()
                if hasattr(lab, 'recruitment_status'):
                    recruitment = lab.recruitment_status
                    return {
                        'is_recruiting_phd': recruitment.is_recruiting_phd,
                        'is_recruiting_postdoc': recruitment.is_recruiting_postdoc,
                        'is_recruiting_intern': recruitment.is_recruiting_intern,
                        'notes': recruitment.notes,
                        'last_updated': recruitment.last_updated
                    }
        except:
            pass
        return None
