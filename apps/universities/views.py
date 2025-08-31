
# apps/universities/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import University, Professor
from .serializers import UniversitySerializer, ProfessorSerializer

class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'state', 'city']
    ordering_fields = ['name', 'ranking']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def professors(self, request, pk=None):
        """Get all professors in a university"""
        university = self.get_object()
        professors = Professor.objects.filter(university=university)
        serializer = ProfessorSerializer(professors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def labs(self, request, pk=None):
        """Get all labs in a university"""
        from apps.labs.models import Lab
        from apps.labs.serializers import LabListSerializer
        
        university = self.get_object()
        labs = Lab.objects.filter(university=university)
        serializer = LabListSerializer(labs, many=True)
        return Response(serializer.data)


class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Professor.objects.select_related('university')
    serializer_class = ProfessorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'research_interests']