
# apps/universities/serializers.py
from rest_framework import serializers
from .models import University, Professor

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class ProfessorSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='university.name', read_only=True)
    
    class Meta:
        model = Professor
        fields = '__all__'

