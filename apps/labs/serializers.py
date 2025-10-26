
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


class LabMinimalSerializer(serializers.ModelSerializer):
    """Minimal fields for write review dropdown"""
    professor_name = serializers.CharField(source='professor.name', read_only=True)

    class Meta:
        model = Lab
        fields = ['id', 'name', 'professor_name']


class LabListSerializer(serializers.ModelSerializer):
    """Full fields for lab search/cards"""
    professor_names = serializers.SerializerMethodField()
    head_professor_name = serializers.CharField(source='head_professor.name', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)
    recruitment_status = RecruitmentStatusSerializer(read_only=True)

    # Use the most appropriate department field - prefer local_name if available
    department = serializers.SerializerMethodField()

    class Meta:
        model = Lab
        fields = ['id', 'name', 'head_professor', 'professor_names', 'head_professor_name',
                 'university_name', 'department', 'research_group_name', 'overall_rating', 'review_count',
                 'research_areas', 'tags', 'recruitment_status', 'university_department',
                 'university', 'description', 'website', 'lab_size']
        extra_kwargs = {
            'head_professor': {'write_only': True},
            'university_department': {'write_only': True},
            'university': {'write_only': True},
        }

    def get_professor_names(self, obj):
        """Return list of all professor names"""
        professor_names = []

        # Get professors from the N:1 relationship (professors.filter(lab=obj))
        try:
            for prof in obj.professors.all():
                professor_names.append(prof.name)
        except:
            pass

        return professor_names

    def get_department(self, obj):
        """Return the best available department name"""
        if obj.university_department:
            # Prefer local_name if available, otherwise use department name
            return obj.university_department.local_name or obj.university_department.department.name
        # Fallback to legacy department field
        return obj.department or ''


class LabDetailSerializer(serializers.ModelSerializer):
    head_professor = ProfessorSerializer(read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    university_department_name = serializers.CharField(source='university_department.university.name', read_only=True)
    department_name = serializers.CharField(source='university_department.department.name', read_only=True)
    department_local_name = serializers.CharField(source='university_department.local_name', read_only=True)
    research_group_name = serializers.CharField(source='research_group.name', read_only=True)
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

