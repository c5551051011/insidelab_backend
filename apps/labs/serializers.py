
# apps/labs/serializers.py
from rest_framework import serializers
from .models import Lab, ResearchTopic, Publication, RecruitmentStatus
from apps.universities.serializers import ProfessorSerializer

class ResearchTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchTopic
        fields = ['id', 'title', 'description', 'keywords', 'funding_info']


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = ['id', 'title', 'authors', 'venue', 'year', 'url', 'citations']


class RecruitmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentStatus
        fields = ['is_recruiting_phd', 'is_recruiting_postdoc', 
                 'is_recruiting_intern', 'notes', 'last_updated']


class LabListSerializer(serializers.ModelSerializer):
    professor_name = serializers.CharField(source='professor.name', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)
    recruitment_status = RecruitmentStatusSerializer(read_only=True)
    university_department_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    department_local_name = serializers.CharField(source='university_department.local_name', read_only=True)

    class Meta:
        model = Lab
        fields = ['id', 'name', 'professor', 'professor_name', 'university', 'university_name',
                 'department', 'research_group', 'research_group_name', 'description', 'website',
                 'lab_size', 'overall_rating', 'review_count', 'research_areas', 'tags', 'recruitment_status',
                 'university_department', 'university_department_name', 'department_name', 'department_local_name']
        extra_kwargs = {
            'professor': {'write_only': True},
            'university': {'write_only': True},
            'research_group': {'write_only': True},
            'university_department': {'write_only': True}
        }


class LabDetailSerializer(serializers.ModelSerializer):
    professor = ProfessorSerializer(read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    university_department_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    department_local_name = serializers.CharField(source='university_department.local_name', read_only=True)
    research_topics = ResearchTopicSerializer(many=True, read_only=True)
    recent_publications = PublicationSerializer(many=True, read_only=True)
    recruitment_status = RecruitmentStatusSerializer(read_only=True)
    rating_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Lab
        fields = '__all__'
    
    def get_rating_breakdown(self, obj):
        # Calculate rating breakdown from reviews
        from apps.reviews.models import Review
        reviews = Review.objects.filter(lab=obj)

        if not reviews.exists():
            return None

        categories = [
            'Mentorship Quality',
            'Research Environment',
            'Work-Life Balance',
            'Career Support',
            'Funding & Resources',
            'Collaboration Culture'
        ]

        breakdown = {}
        for category in categories:
            ratings = []
            for review in reviews:
                category_ratings_dict = review.category_ratings_dict
                if category in category_ratings_dict:
                    ratings.append(category_ratings_dict[category])

            if ratings:
                breakdown[category] = sum(ratings) / len(ratings)

        return breakdown

