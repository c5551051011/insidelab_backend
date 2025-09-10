
# apps/reviews/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review, ReviewHelpful

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    user_position = serializers.CharField(source='user.position', read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user', 'helpful_count', 'is_verified')
    
    def validate_category_ratings(self, value):
        required_categories = [
            'Mentorship Quality',
            'Research Environment',
            'Work-Life Balance',
            'Career Support',
            'Funding & Resources',
            'Collaboration Culture'
        ]
        
        for category in required_categories:
            if category not in value:
                raise serializers.ValidationError(
                    f"Missing rating for {category}"
                )
            if not (0 <= value[category] <= 5):
                raise serializers.ValidationError(
                    f"Rating for {category} must be between 0 and 5"
                )
        
        return value
    
    def validate_pros(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one pro is required")
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 pros allowed")
        return value
    
    def validate_cons(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 cons allowed")
        return value


class ReviewHelpfulSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewHelpful
        fields = ['review', 'is_helpful']
        read_only_fields = ('user',)