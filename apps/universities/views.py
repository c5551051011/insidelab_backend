
# apps/universities/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .models import University, Professor, ResearchGroup, UniversityDepartment, Department
from .serializers import UniversitySerializer, ProfessorSerializer, ResearchGroupSerializer, UniversityDepartmentSerializer, DepartmentSerializer
from apps.utils.cache import cache_response, CacheManager

class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'state', 'city']
    ordering_fields = ['name', 'ranking']
    ordering = ['name']

    @action(detail=True, methods=['get', 'post'])
    def departments(self, request, pk=None):
        """Get all departments in a university or add a new department to a university"""
        university = self.get_object()

        if request.method == 'GET':
            # Try to get from cache first
            cached_data = CacheManager.get_university_departments(university.id)
            if cached_data is not None:
                return Response(cached_data)

            university_departments = UniversityDepartment.objects.filter(
                university=university,
                is_active=True
            ).select_related('department', 'university').order_by('department__name')

            serializer = UniversityDepartmentSerializer(university_departments, many=True)

            # Cache the response
            CacheManager.set_university_departments(university.id, serializer.data)

            return Response(serializer.data)

        elif request.method == 'POST':
            # Add a new department to this university
            # Support two flows:
            # 1. Existing: {"department": 2, "local_name": "..."}
            # 2. Enhanced: {"department_name": "Physics", "description": "...", "local_name": "..."}

            department_name = request.data.get('department_name')

            if department_name:
                # Enhanced flow: Auto-create department if needed
                department, created = Department.objects.get_or_create(
                    name=department_name,
                    defaults={
                        'description': request.data.get('description', f'Department of {department_name}'),
                        'common_names': request.data.get('common_names', [])
                    }
                )

                # Prepare data for UniversityDepartment creation
                serializer_data = request.data.copy()
                serializer_data['department'] = department.id
                serializer_data['university'] = university.id

                # Remove department creation fields to avoid serializer errors
                serializer_data.pop('department_name', None)
                serializer_data.pop('description', None)
                serializer_data.pop('common_names', None)

                serializer = UniversityDepartmentSerializer(data=serializer_data)
                if serializer.is_valid():
                    university_dept = serializer.save(university=university)

                    # Return enhanced response with department creation info
                    response_data = serializer.data
                    response_data['department_created'] = created
                    response_data['department_info'] = {
                        'id': department.id,
                        'name': department.name,
                        'description': department.description,
                        'common_names': department.common_names
                    }

                    return Response(response_data, status=201)
                return Response(serializer.errors, status=400)

            else:
                # Existing flow: Use department ID
                serializer = UniversityDepartmentSerializer(data=request.data)
                if serializer.is_valid():
                    # Ensure the university matches the URL parameter
                    serializer.save(university=university)

                    # Clear cache for this university (simplified approach)
                    # CacheManager.delete_university_departments(university.id)

                    return Response(serializer.data, status=201)
                return Response(serializer.errors, status=400)

    @cache_response('PROFESSORS')
    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """Get all professors in a university"""
        university = self.get_object()
        professors = Professor.objects.filter(
            university_department__university=university
        ).select_related('university_department__department', 'research_group')
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)

    @cache_response('LABS')
    @action(detail=True, methods=['get'])
    def labs(self, request, pk=None):
        """Get all labs in a university"""
        from apps.labs.models import Lab
        from apps.labs.serializers import LabListSerializer

        university = self.get_object()
        labs = Lab.objects.filter(
            university_department__university=university
        ).select_related('professor', 'university_department__department', 'research_group')
        serializer = LabListSerializer(labs, many=True)
        return Response(serializer.data)


class ResearchGroupViewSet(viewsets.ModelViewSet):
    queryset = ResearchGroup.objects.select_related(
        'university_department__university',
        'university_department__department',
        'head_professor'
    ).prefetch_related('professors', 'labs')
    serializer_class = ResearchGroupSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university_department__university', 'university_department__department', 'university_department']
    search_fields = ['name', 'description', 'research_areas']
    ordering_fields = ['name', 'created_at', 'professor_count', 'lab_count']
    ordering = ['university_department__university__name', 'university_department__department__name', 'name']

    @cache_response('PROFESSORS')
    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """Get all professors in this research group"""
        group = self.get_object()
        professors = group.professors.all()
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)

    @cache_response('LABS')
    @action(detail=True, methods=['get'])
    def labs(self, request, pk=None):
        """Get all labs in this research group"""
        from apps.labs.models import Lab
        from apps.labs.serializers import LabListSerializer

        group = self.get_object()
        labs = group.labs.all()
        serializer = LabListSerializer(labs, many=True)
        return Response(serializer.data)


class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.select_related(
        'university_department__university',
        'university_department__department',
        'research_group'
    )
    serializer_class = ProfessorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university_department__university', 'university_department__department', 'research_group']
    search_fields = ['name', 'research_interests']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'common_names']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def universities(self, request, pk=None):
        """Get all universities that have this department"""
        department = self.get_object()
        university_departments = UniversityDepartment.objects.filter(
            department=department,
            is_active=True
        ).select_related('university', 'department')

        serializer = UniversityDepartmentSerializer(university_departments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """Get all professors in this department across all universities"""
        department = self.get_object()
        professors = Professor.objects.filter(
            university_department__department=department
        ).select_related('university_department__university', 'research_group')

        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)