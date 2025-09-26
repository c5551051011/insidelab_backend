
# apps/universities/serializers.py
from rest_framework import serializers
from .models import University, Professor, ResearchGroup


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


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


class ProfessorSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)

    class Meta:
        model = Professor
        fields = '__all__'

