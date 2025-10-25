
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
    lab = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = ['id', 'name', 'email', 'lab']

    def get_lab(self, obj):
        """Return lab this professor belongs to"""
        try:
            if obj.lab:
                return {
                    'id': obj.lab.id,
                    'name': obj.lab.name
                }

            # Fallback to legacy labs for backward compatibility
            if hasattr(obj, 'legacy_labs') and obj.legacy_labs.exists():
                lab = obj.legacy_labs.first()
                return {
                    'id': lab.id,
                    'name': lab.name
                }

            if hasattr(obj, 'headed_labs') and obj.headed_labs.exists():
                lab = obj.headed_labs.first()
                return {
                    'id': lab.id,
                    'name': lab.name
                }
        except Exception as e:
            # For debugging, you might want to log this error
            pass

        return None


class ProfessorSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)
    lab_info = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = '__all__'

    def get_lab_info(self, obj):
        """Return lab this professor belongs to"""
        if obj.lab:
            return {
                'id': obj.lab.id,
                'name': obj.lab.name
            }

        # Fallback to legacy labs for backward compatibility
        try:
            if obj.legacy_labs.exists():
                lab = obj.legacy_labs.first()
                return {
                    'id': lab.id,
                    'name': lab.name
                }
        except:
            pass

        try:
            if obj.headed_labs.exists():
                lab = obj.headed_labs.first()
                return {
                    'id': lab.id,
                    'name': lab.name
                }
        except:
            pass

        return None

