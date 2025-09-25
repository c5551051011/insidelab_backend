
# apps/universities/serializers.py
from rest_framework import serializers
from .models import University, Professor, ResearchGroup


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class ResearchGroupSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)
    head_professor_name = serializers.CharField(source='head_professor.name', read_only=True)
    professor_count = serializers.SerializerMethodField()
    lab_count = serializers.SerializerMethodField()

    class Meta:
        model = ResearchGroup
        fields = [
            'id', 'name', 'university', 'university_name', 'department',
            'description', 'website', 'research_areas', 'head_professor',
            'head_professor_name', 'professor_count', 'lab_count',
            'created_at', 'updated_at'
        ]

    def get_professor_count(self, obj):
        return obj.professors.count()

    def get_lab_count(self, obj):
        return obj.labs.count()


class ProfessorSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)

    class Meta:
        model = Professor
        fields = '__all__'

