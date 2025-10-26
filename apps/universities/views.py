
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
from .serializers import UniversityMinimalSerializer, UniversitySerializer, ProfessorMinimalSerializer, ProfessorSerializer, ResearchGroupMinimalSerializer, ResearchGroupSerializer, UniversityDepartmentMinimalSerializer, UniversityDepartmentSerializer, DepartmentSerializer, DepartmentMinimalSerializer
from apps.utils.cache import cache_response, CacheManager

class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'state', 'city']
    ordering_fields = ['name', 'ranking']
    ordering = ['name']

    @cache_response('UNIVERSITIES', timeout=60*60*24)  # Cache for 24 hours
    def list(self, request, *args, **kwargs):
        """Override list to add caching for university list"""
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        # Check for fields parameter to determine serializer
        fields = self.request.query_params.get('fields', 'full')
        if fields == 'minimal':
            return UniversityMinimalSerializer
        return UniversitySerializer

    @action(detail=True, methods=['get', 'post'])
    def departments(self, request, pk=None):
        """Get all departments in a university or add a new department to a university"""
        university = self.get_object()

        if request.method == 'GET':
            # Check for fields parameter first
            fields = request.query_params.get('fields', 'full')

            # Try to get from cache first (only for full version)
            if fields != 'minimal':
                cached_data = CacheManager.get_university_departments(university.id)
                if cached_data is not None:
                    return Response(cached_data)

            university_departments = UniversityDepartment.objects.filter(
                university=university,
                is_active=True
            ).select_related('department', 'university').order_by('department__name')

            # Use serializer based on fields parameter
            if fields == 'minimal':
                serializer = UniversityDepartmentMinimalSerializer(university_departments, many=True)
            else:
                serializer = UniversityDepartmentSerializer(university_departments, many=True)

            # Cache the response (only cache full version to avoid complexity)
            if fields != 'minimal':
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

                # Set local_name to department.name if not provided
                if not serializer_data.get('local_name'):
                    serializer_data['local_name'] = department.name

                # Remove department creation fields to avoid serializer errors
                serializer_data.pop('department_name', None)
                serializer_data.pop('description', None)
                serializer_data.pop('common_names', None)

                # Check if UniversityDepartment already exists
                existing_university_dept = UniversityDepartment.objects.filter(
                    university=university,
                    department=department
                ).first()

                if existing_university_dept:
                    # Return existing data instead of error
                    serializer = UniversityDepartmentSerializer(existing_university_dept)
                    response_data = serializer.data
                    response_data['department_created'] = created
                    response_data['university_department_created'] = False
                    response_data['department_info'] = {
                        'id': department.id,
                        'name': department.name,
                        'description': department.description,
                        'common_names': department.common_names
                    }
                    return Response(response_data, status=200)

                # Create new UniversityDepartment
                serializer = UniversityDepartmentSerializer(data=serializer_data)
                if serializer.is_valid():
                    university_dept = serializer.save(university=university)

                    # Clear cache for this university
                    CacheManager.delete_university_departments(university.id)

                    # Return enhanced response with department creation info
                    response_data = serializer.data
                    response_data['department_created'] = created
                    response_data['university_department_created'] = True
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
                department_id = request.data.get('department')
                if department_id:
                    # Check if UniversityDepartment already exists
                    existing_university_dept = UniversityDepartment.objects.filter(
                        university=university,
                        department_id=department_id
                    ).first()

                    if existing_university_dept:
                        # Return existing data instead of error
                        serializer = UniversityDepartmentSerializer(existing_university_dept)
                        response_data = serializer.data
                        response_data['university_department_created'] = False
                        return Response(response_data, status=200)

                    # Create new UniversityDepartment
                    serializer_data = request.data.copy()

                    # Set local_name to department.name if not provided
                    if not serializer_data.get('local_name'):
                        from .models import Department
                        department = Department.objects.get(id=department_id)
                        serializer_data['local_name'] = department.name

                    serializer = UniversityDepartmentSerializer(data=serializer_data)
                    if serializer.is_valid():
                        # Ensure the university matches the URL parameter
                        serializer.save(university=university)

                        # Clear cache for this university (simplified approach)
                        CacheManager.delete_university_departments(university.id)

                        response_data = serializer.data
                        response_data['university_department_created'] = True
                        return Response(response_data, status=201)
                    return Response(serializer.errors, status=400)
                else:
                    return Response({"error": "Either department_name or department ID is required"}, status=400)

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

    def get_serializer_class(self):
        # Check for fields parameter to determine serializer
        fields = self.request.query_params.get('fields', 'full')
        if fields == 'minimal':
            return ResearchGroupMinimalSerializer
        return ResearchGroupSerializer

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
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university_department__university', 'university_department__department', 'research_group']
    search_fields = ['name', 'research_interests']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        # Check for fields parameter to optimize queries
        fields = self.request.query_params.get('fields', 'full')

        if fields == 'minimal':
            # For minimal fields, select lab and prefetch legacy relationships
            return Professor.objects.select_related(
                'university_department__university',
                'university_department__department',
                'research_group',
                'lab'
            ).prefetch_related('headed_labs')
        else:
            # For full fields
            return Professor.objects.select_related(
                'university_department__university',
                'university_department__department',
                'research_group',
                'lab'
            ).prefetch_related('headed_labs')

    def get_serializer_class(self):
        # Check for fields parameter to determine serializer
        fields = self.request.query_params.get('fields', 'full')
        if fields == 'minimal':
            return ProfessorMinimalSerializer
        return ProfessorSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'common_names']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        # Check for fields parameter to determine serializer
        fields = self.request.query_params.get('fields', 'full')
        if fields == 'minimal':
            return DepartmentMinimalSerializer
        return DepartmentSerializer

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