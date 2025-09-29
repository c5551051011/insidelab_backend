# apps/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import secrets
from .models import UserLabInterest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='joined_date', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    university_department_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'name', 'university', 'university_name',
                 'university_department', 'university_department_name', 'department_name',
                 'position', 'department', 'lab_name', 'is_verified', 'verification_status',
                 'is_lab_member', 'can_provide_services', 'review_count', 'helpful_votes',
                 'joined_date', 'created_at')
        read_only_fields = ('is_verified', 'verification_status', 'joined_date', 'created_at',
                           'review_count', 'helpful_votes', 'university_name', 'university_department_name',
                           'department_name')
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
                 'name', 'position', 'university_department', 'department')
    
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
    """Serializer for user lab interests"""
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    lab_professor = serializers.CharField(source='lab.professor.name', read_only=True)
    lab_university = serializers.CharField(source='lab.university_department.university.name', read_only=True)
    lab_department = serializers.CharField(source='lab.university_department.department.name', read_only=True)
    lab_rating = serializers.DecimalField(source='lab.overall_rating', max_digits=3, decimal_places=2, read_only=True)
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)

    class Meta:
        model = UserLabInterest
        fields = [
            'id', 'lab', 'lab_name', 'lab_professor', 'lab_university', 'lab_department', 'lab_rating',
            'interest_type', 'notes', 'created_at', 'updated_at', 'user_display_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_display_name']

    def create(self, validated_data):
        # Auto-assign the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


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