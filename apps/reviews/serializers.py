
# apps/reviews/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review, ReviewHelpful, RatingCategory, ReviewRating

User = get_user_model()


class RatingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingCategory
        fields = ['id', 'name', 'display_name', 'description', 'sort_order']


class ReviewRatingSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    category_id = serializers.IntegerField(source='category.id', read_only=True)

    class Meta:
        model = ReviewRating
        fields = ['category_id', 'category_name', 'rating']


class ReviewSerializer(serializers.ModelSerializer):
    user_position = serializers.CharField(source='user.position', read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    category_ratings = serializers.SerializerMethodField()
    ratings_input = serializers.DictField(write_only=True, required=True)
    professor_name = serializers.CharField(source='professor.name', read_only=True)
    lab_name = serializers.CharField(source='lab.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'professor', 'professor_name', 'lab', 'lab_name', 'user', 'position', 'duration', 'rating',
            'category_ratings', 'ratings_input', 'review_text', 'pros', 'cons',
            'is_verified', 'helpful_count', 'created_at', 'updated_at',
            'user_position'
        ]
        read_only_fields = ('user', 'helpful_count', 'is_verified', 'category_ratings', 'professor_name', 'lab_name')
        extra_kwargs = {
            'professor': {'required': True},
            'lab': {'required': False}
        }

    def get_category_ratings(self, obj):
        """Return category ratings as a dictionary for API responses"""
        return obj.category_ratings_dict

    def validate_ratings_input(self, value):
        """Validate the category ratings input"""
        active_categories = RatingCategory.objects.filter(is_active=True)
        active_category_names = set(cat.display_name for cat in active_categories)

        for category_name, rating in value.items():
            if category_name not in active_category_names:
                raise serializers.ValidationError(
                    f"Invalid category: {category_name}"
                )
            if not (0 <= rating <= 5):
                raise serializers.ValidationError(
                    f"Rating for {category_name} must be between 0 and 5"
                )

        # Check that all required categories are provided
        missing_categories = active_category_names - set(value.keys())
        if missing_categories:
            raise serializers.ValidationError(
                f"Missing ratings for: {', '.join(missing_categories)}"
            )

        return value

    def create(self, validated_data):
        ratings_input = validated_data.pop('ratings_input')
        review = super().create(validated_data)
        review.set_category_ratings(ratings_input)
        return review

    def update(self, instance, validated_data):
        if 'ratings_input' in validated_data:
            ratings_input = validated_data.pop('ratings_input')
            instance.set_category_ratings(ratings_input)
        return super().update(instance, validated_data)
    
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

    def validate_professor(self, value):
        if value is None:
            raise serializers.ValidationError("Professor is required")
        return value


class ReviewHelpfulSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewHelpful
        fields = ['review', 'is_helpful']
        read_only_fields = ('user',)