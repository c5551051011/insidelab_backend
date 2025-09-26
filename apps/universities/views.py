
# apps/universities/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import University, Professor, ResearchGroup
from .serializers import UniversitySerializer, ProfessorSerializer, ResearchGroupSerializer

class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'state', 'city']
    ordering_fields = ['name', 'ranking']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """Get all professors in a university"""
        university = self.get_object()
        professors = Professor.objects.filter(university_department__university=university)
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def labs(self, request, pk=None):
        """Get all labs in a university"""
        from apps.labs.models import Lab
        from apps.labs.serializers import LabListSerializer

        university = self.get_object()
        labs = Lab.objects.filter(university_department__university=university)
        serializer = LabListSerializer(labs, many=True)
        return Response(serializer.data)


class ResearchGroupViewSet(viewsets.ModelViewSet):
    queryset = ResearchGroup.objects.select_related(
        'university_department__university',
        'university_department__department',
        'head_professor'
    ).prefetch_related('professors', 'labs')
    serializer_class = ResearchGroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university_department__university', 'university_department__department']
    search_fields = ['name', 'description', 'research_areas']
    ordering_fields = ['name', 'created_at', 'professor_count', 'lab_count']
    ordering = ['university_department__university__name', 'university_department__department__name', 'name']

    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """Get all professors in this research group"""
        group = self.get_object()
        professors = group.professors.all()
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)

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