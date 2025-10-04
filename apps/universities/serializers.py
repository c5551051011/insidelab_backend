
# apps/universities/serializers.py
from rest_framework import serializers
from .models import University, Professor, ResearchGroup, UniversityDepartment, Department


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    university_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'common_names', 'university_count', 'created_at']

    def get_university_count(self, obj):
        return obj.university_departments.filter(is_active=True).count()


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

    def create(self, validated_data):
        # Create the instance using direct database insert to bypass property conflicts
        university_department = validated_data.get('university_department')
        if university_department:
            from django.db import connection
            import json

            # Insert directly to database to avoid property conflicts
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO research_groups
                (name, description, website, research_areas, department, university_id, university_department_id, created_at, updated_at, head_professor_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
                RETURNING id
            ''', [
                validated_data['name'],
                validated_data.get('description', ''),
                validated_data.get('website', ''),
                json.dumps(validated_data.get('research_areas', [])),
                university_department.department.name,  # Legacy field
                university_department.university.id,    # Legacy field
                university_department.id,              # New field
                validated_data.get('head_professor', {}).get('id') if validated_data.get('head_professor') else None
            ])

            new_id = cursor.fetchone()[0]
            return ResearchGroup.objects.get(id=new_id)

        return super().create(validated_data)

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

