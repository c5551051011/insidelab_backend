# apps/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import secrets
from .models import UserLabInterest, UserResearchProfile

User = get_user_model()


class UserResearchProfileSerializer(serializers.ModelSerializer):
    """Serializer for user research profile"""

    class Meta:
        model = UserResearchProfile
        fields = [
            'id', 'primary_research_area', 'specialties_interests', 'research_keywords',
            'academic_background', 'research_goals', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Auto-assign the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='joined_date', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    university_department_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    research_profile = UserResearchProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'name', 'university', 'university_name',
                 'university_department', 'university_department_name', 'department_name',
                 'position', 'department', 'lab_name', 'research_profile', 'is_verified', 'verification_status',
                 'is_lab_member', 'can_provide_services', 'review_count', 'helpful_votes',
                 'language', 'joined_date', 'created_at')
        read_only_fields = ('is_verified', 'verification_status', 'joined_date', 'created_at',
                           'review_count', 'helpful_votes', 'university_name', 'university_department_name',
                           'department_name', 'research_profile')
        extra_kwargs = {
            'university': {'write_only': True},
            'university_department': {'write_only': True}
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password_confirm',
                 'name', 'position', 'university_department', 'department', 'language')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Generate verification token
        validated_data['verification_token'] = secrets.token_urlsafe(32)
        validated_data['verification_status'] = 'pending'
        
        user = User.objects.create_user(**validated_data)
        # TODO: Send verification email
        return user


class UserLabInterestSerializer(serializers.ModelSerializer):
    """Serializer for user lab interests with detailed lab information"""
    # Required fields
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    professor_name = serializers.CharField(source='lab.head_professor.name', read_only=True)
    university_name = serializers.CharField(source='lab.university_department.university.name', read_only=True)

    # Optional fields
    department = serializers.CharField(source='lab.university_department.department.name', read_only=True)
    research_group = serializers.CharField(source='lab.research_group.name', read_only=True)
    overall_rating = serializers.DecimalField(source='lab.overall_rating', max_digits=3, decimal_places=2, read_only=True)
    review_count = serializers.IntegerField(source='lab.review_count', read_only=True)
    research_areas = serializers.ListField(source='lab.research_areas', read_only=True)
    tags = serializers.ListField(source='lab.tags', read_only=True)
    description = serializers.CharField(source='lab.description', read_only=True)
    website = serializers.URLField(source='lab.website', read_only=True)

    # User interest specific fields
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)

    class Meta:
        model = UserLabInterest
        fields = [
            # UserLabInterest fields
            'id', 'lab', 'interest_type', 'notes', 'created_at', 'updated_at', 'user_display_name',
            # Lab fields - required
            'lab_name', 'professor_name', 'university_name',
            # Lab fields - optional
            'department', 'research_group', 'overall_rating', 'review_count',
            'research_areas', 'tags', 'description', 'website'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_display_name']

    def create(self, validated_data):
        # Auto-assign the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserLabInterestMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for user lab interests - only IDs"""

    class Meta:
        model = UserLabInterest
        fields = ['id', 'lab']


class UserLabInterestCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating lab interests"""

    class Meta:
        model = UserLabInterest
        fields = ['lab', 'interest_type', 'notes']

    def create(self, validated_data):
        # Auto-assign the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        # Check if user already has interest in this lab
        user = self.context['request'].user
        lab = attrs['lab']

        if UserLabInterest.objects.filter(user=user, lab=lab).exists():
            # If updating, allow it
            if self.instance:
                return attrs
            raise serializers.ValidationError("You already have an interest recorded for this lab.")

        return attrs