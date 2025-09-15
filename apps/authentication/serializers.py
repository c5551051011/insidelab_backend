# apps/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import secrets

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='joined_date', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'name', 'university', 'position',
                 'department', 'lab_name', 'is_verified', 'verification_status',
                 'is_lab_member', 'can_provide_services', 'review_count', 'helpful_votes',
                 'joined_date', 'created_at')
        read_only_fields = ('is_verified', 'verification_status', 'joined_date', 'created_at',
                           'review_count', 'helpful_votes')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm',
                 'name', 'position', 'department')
    
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