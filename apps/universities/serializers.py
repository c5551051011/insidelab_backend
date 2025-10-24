
# apps/universities/serializers.py
from rest_framework import serializers
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
        fields = ['id', 'name']


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
    labs = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = ['id', 'name', 'email', 'labs']

    def get_labs(self, obj):
        """Return labs associated with this professor"""
        labs_data = []

        # Get labs from the new professors ManyToMany relationship
        try:
            for lab in obj.labs.all():
                labs_data.append({
                    'id': lab.id,
                    'name': lab.name
                })
        except:
            pass

        # Also check legacy labs and headed_labs
        try:
            for lab in obj.legacy_labs.all():
                lab_data = {'id': lab.id, 'name': lab.name}
                if lab_data not in labs_data:
                    labs_data.append(lab_data)
        except:
            pass

        try:
            for lab in obj.headed_labs.all():
                lab_data = {'id': lab.id, 'name': lab.name}
                if lab_data not in labs_data:
                    labs_data.append(lab_data)
        except:
            pass

        return labs_data


class ProfessorSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)

    class Meta:
        model = Professor
        fields = '__all__'

