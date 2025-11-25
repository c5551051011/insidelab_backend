# apps/interviews/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MockInterviewSession, SessionLab, SessionTimeSlot, SessionResearchArea, InterviewReview
from apps.labs.models import Lab
from apps.publications.models import ResearchArea

User = get_user_model()


class SessionTimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for preferred time slots"""

    class Meta:
        model = SessionTimeSlot
        fields = ['date', 'time', 'priority']


class SessionResearchAreaSerializer(serializers.ModelSerializer):
    """Serializer for research areas"""
    research_area_name = serializers.CharField(source='research_area.name', read_only=True)
    department_name = serializers.CharField(source='research_area.department.name', read_only=True)

    class Meta:
        model = SessionResearchArea
        fields = ['research_area', 'research_area_name', 'department_name', 'priority']


class SessionLabSerializer(serializers.ModelSerializer):
    """Serializer for target labs"""
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    university_name = serializers.CharField(source='lab.university.name', read_only=True)
    department_name = serializers.CharField(source='lab.university_department.department.name', read_only=True)
    head_professor_name = serializers.CharField(source='lab.head_professor.name', read_only=True)

    class Meta:
        model = SessionLab
        fields = ['lab', 'lab_name', 'university_name', 'department_name',
                  'head_professor_name', 'priority']


class InterviewerSerializer(serializers.ModelSerializer):
    """Serializer for interviewer details"""
    lab_name = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    research_areas = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'position',
            'university', 'department', 'lab_name', 'bio', 'profile_image',
            'average_rating', 'review_count', 'recent_reviews',
            'education', 'research_areas'
        ]

    def get_lab_name(self, obj):
        """Get interviewer's lab name"""
        # Try to get from professor profile first
        if hasattr(obj, 'professor_profile'):
            professor = obj.professor_profile
            if professor.lab:
                return professor.lab.name
        return None

    def get_bio(self, obj):
        """Get interviewer's bio"""
        if hasattr(obj, 'professor_profile') and obj.professor_profile:
            return obj.professor_profile.bio
        return ""

    def get_profile_image(self, obj):
        """Get interviewer's profile image"""
        if hasattr(obj, 'professor_profile') and obj.professor_profile:
            return obj.professor_profile.profile_image_url
        return None

    def get_average_rating(self, obj):
        """Get interviewer's average rating"""
        if hasattr(obj, 'professor_profile') and obj.professor_profile:
            return float(obj.professor_profile.overall_rating) if obj.professor_profile.overall_rating else 0.0
        return 0.0

    def get_review_count(self, obj):
        """Get interviewer's review count"""
        if hasattr(obj, 'professor_profile') and obj.professor_profile:
            return obj.professor_profile.review_count
        return 0

    def get_recent_reviews(self, obj):
        """Get recent reviews for interviewer"""
        if hasattr(obj, 'professor_profile') and obj.professor_profile:
            from apps.reviews.models import Review
            recent_reviews = Review.objects.filter(
                professor=obj.professor_profile,
                status='active'
            ).order_by('-created_at')[:3]

            return [
                {
                    'rating': review.rating,
                    'comment': review.comment[:100] + ('...' if len(review.comment) > 100 else '')
                }
                for review in recent_reviews
            ]
        return []

    def get_education(self, obj):
        """Get interviewer's education background"""
        if hasattr(obj, 'research_profile') and obj.research_profile:
            education_list = []
            profile = obj.research_profile

            if profile.phd_university:
                education_list.append(f"PhD in {profile.phd_field or 'Research'} - {profile.phd_university}")
            if profile.masters_university:
                education_list.append(f"MS in {profile.masters_field or 'Research'} - {profile.masters_university}")
            if profile.bachelors_university:
                education_list.append(f"BS in {profile.bachelors_field or 'Research'} - {profile.bachelors_university}")

            return education_list
        return []

    def get_research_areas(self, obj):
        """Get interviewer's research areas"""
        if hasattr(obj, 'research_profile') and obj.research_profile:
            return obj.research_profile.research_interests or []
        return []


class MockInterviewSessionListSerializer(serializers.ModelSerializer):
    """Serializer for listing sessions (lighter weight)"""
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    interviewer_email = serializers.CharField(source='interviewer.email', read_only=True, allow_null=True)

    # Add summary information for research areas and labs
    research_area_count = serializers.SerializerMethodField()
    target_lab_count = serializers.SerializerMethodField()
    preferred_slot_count = serializers.SerializerMethodField()
    primary_research_area = serializers.SerializerMethodField()
    primary_lab = serializers.SerializerMethodField()

    # Add actual lists for quick overview
    research_area_names = serializers.SerializerMethodField()
    target_lab_names = serializers.SerializerMethodField()
    preferred_slot_summary = serializers.SerializerMethodField()

    # Add missing fields
    focus_areas = serializers.CharField(read_only=True)
    interviewer = serializers.SerializerMethodField()
    zoom_link = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    confirmed_time_formatted = serializers.SerializerMethodField()

    class Meta:
        model = MockInterviewSession
        fields = [
            'id', 'session_type', 'session_type_display', 'status', 'status_display',
            'confirmed_date', 'confirmed_time', 'confirmed_time_formatted', 'total_price',
            'interviewer_email', 'interviewer', 'match_type', 'created_at', 'updated_at',
            'research_area_count', 'target_lab_count', 'preferred_slot_count',
            'primary_research_area', 'primary_lab',
            'research_area_names', 'target_lab_names', 'preferred_slot_summary',
            'focus_areas', 'zoom_link', 'completed_at'
        ]

    def get_research_area_count(self, obj):
        return obj.research_areas.count()

    def get_target_lab_count(self, obj):
        return obj.target_labs.count()

    def get_preferred_slot_count(self, obj):
        return obj.preferred_slots.count()

    def get_primary_research_area(self, obj):
        """Get the first priority research area"""
        primary = obj.research_areas.filter(priority=1).first()
        return primary.research_area.name if primary else None

    def get_primary_lab(self, obj):
        """Get the first priority lab"""
        primary = obj.target_labs.filter(priority=1).first()
        return primary.lab.name if primary else None

    def get_research_area_names(self, obj):
        """Get list of research area names ordered by priority"""
        return [
            {
                'name': ra.research_area.name,
                'priority': ra.priority
            }
            for ra in obj.research_areas.all().order_by('priority')
        ]

    def get_target_lab_names(self, obj):
        """Get list of lab names ordered by priority"""
        return [
            {
                'name': lab.lab.name,
                'university_name': lab.lab.university.name if lab.lab.university else '',
                'field_name': self._get_lab_field_name(lab.lab),
                'priority': lab.priority
            }
            for lab in obj.target_labs.all().order_by('priority')
        ]

    def get_preferred_slot_summary(self, obj):
        """Get formatted preferred time slots"""
        slots = []
        for slot in obj.preferred_slots.all().order_by('priority'):
            # Format as "2024-11-15 at 2:00 PM"
            date_str = slot.date.strftime('%Y-%m-%d')
            time_str = slot.time.strftime('%-I:%M %p')  # 2:00 PM format
            slots.append(f"{date_str} at {time_str}")
        return slots

    def _get_lab_field_name(self, lab):
        """Helper to get lab's field/department name"""
        if lab.university_department and lab.university_department.department:
            return lab.university_department.department.name
        return lab.department or 'Research'

    def get_interviewer(self, obj):
        """Get detailed interviewer info only if status is confirmed/completed"""
        if obj.status in ['confirmed', 'completed'] and obj.interviewer:
            return InterviewerSerializer(obj.interviewer).data
        return None

    def get_zoom_link(self, obj):
        """Get zoom link if session is confirmed"""
        if obj.status in ['confirmed', 'completed'] and obj.zoom_link:
            return obj.zoom_link
        return None

    def get_completed_at(self, obj):
        """Get completion timestamp for completed sessions"""
        if obj.status == 'completed' and obj.completed_at:
            return obj.completed_at
        return None

    def get_confirmed_time_formatted(self, obj):
        """Get formatted confirmed time like '2:00 PM'"""
        if obj.confirmed_time:
            return obj.confirmed_time.strftime('%-I:%M %p')
        return None


class MockInterviewSessionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed session view"""
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    match_type_display = serializers.CharField(source='get_match_type_display', read_only=True, allow_null=True)

    research_areas = SessionResearchAreaSerializer(many=True, read_only=True)
    target_labs = SessionLabSerializer(many=True, read_only=True)
    preferred_slots = SessionTimeSlotSerializer(many=True, read_only=True)
    interviewer = InterviewerSerializer(read_only=True)

    # Add enhanced fields from list serializer
    research_area_names = serializers.SerializerMethodField()
    research_area_count = serializers.SerializerMethodField()
    primary_research_area = serializers.SerializerMethodField()
    target_lab_names = serializers.SerializerMethodField()
    target_lab_count = serializers.SerializerMethodField()
    primary_lab = serializers.SerializerMethodField()
    preferred_slot_summary = serializers.SerializerMethodField()
    preferred_slot_count = serializers.SerializerMethodField()
    zoom_link = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    confirmed_time_formatted = serializers.SerializerMethodField()

    class Meta:
        model = MockInterviewSession
        fields = [
            'id', 'session_type', 'session_type_display', 'status', 'status_display',
            'focus_areas', 'additional_notes', 'match_type', 'match_type_display',
            'interviewer', 'confirmed_date', 'confirmed_time', 'confirmed_time_formatted',
            'total_price', 'created_at', 'updated_at',
            # Enhanced summary fields
            'research_area_names', 'research_area_count', 'primary_research_area',
            'target_lab_names', 'target_lab_count', 'primary_lab',
            'preferred_slot_summary', 'preferred_slot_count',
            'zoom_link', 'completed_at',
            # Legacy detail fields
            'research_areas', 'target_labs', 'preferred_slots'
        ]

    # Copy methods from ListSerializer
    def get_research_area_names(self, obj):
        return [ra.research_area.name for ra in obj.research_areas.all().order_by('priority')]

    def get_research_area_count(self, obj):
        return obj.research_areas.count()

    def get_primary_research_area(self, obj):
        primary = obj.research_areas.filter(priority=1).first()
        return primary.research_area.name if primary else None

    def get_target_lab_names(self, obj):
        return [
            {
                'name': lab.lab.name,
                'university_name': lab.lab.university.name if lab.lab.university else '',
                'field_name': self._get_lab_field_name(lab.lab),
                'priority': lab.priority
            }
            for lab in obj.target_labs.all().order_by('priority')
        ]

    def get_target_lab_count(self, obj):
        return obj.target_labs.count()

    def get_primary_lab(self, obj):
        primary = obj.target_labs.filter(priority=1).first()
        return primary.lab.name if primary else None

    def get_preferred_slot_summary(self, obj):
        slots = []
        for slot in obj.preferred_slots.all().order_by('priority'):
            date_str = slot.date.strftime('%Y-%m-%d')
            time_str = slot.time.strftime('%-I:%M %p')
            slots.append(f"{date_str} at {time_str}")
        return slots

    def get_preferred_slot_count(self, obj):
        return obj.preferred_slots.count()

    def get_zoom_link(self, obj):
        if obj.status in ['confirmed', 'completed'] and obj.zoom_link:
            return obj.zoom_link
        return None

    def get_completed_at(self, obj):
        if obj.status == 'completed' and obj.completed_at:
            return obj.completed_at
        return None

    def get_confirmed_time_formatted(self, obj):
        if obj.confirmed_time:
            return obj.confirmed_time.strftime('%-I:%M %p')
        return None

    def _get_lab_field_name(self, lab):
        if lab.university_department and lab.university_department.department:
            return lab.university_department.department.name
        return lab.department or 'Research'


class MockInterviewSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new sessions"""
    selected_research_areas = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        max_length=3,
        min_length=1,
        help_text='List of research area IDs (max 3)'
    )

    selected_labs = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        max_length=2,
        min_length=1,
        help_text='List of lab IDs (max 2)'
    )

    preferred_slots = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        max_length=3,
        min_length=1,
        help_text='List of preferred time slots with date, time, and priority'
    )

    class Meta:
        model = MockInterviewSession
        fields = [
            'session_type', 'focus_areas', 'additional_notes',
            'total_price', 'selected_research_areas', 'selected_labs', 'preferred_slots'
        ]

    def validate_selected_research_areas(self, value):
        """Validate that research area IDs exist and max 3 areas selected"""
        if len(value) > 3:
            raise serializers.ValidationError("Maximum 3 research areas can be selected")

        if len(value) == 0:
            raise serializers.ValidationError("At least 1 research area must be selected")

        # Check if all research areas exist
        existing_areas = ResearchArea.objects.filter(id__in=value).count()
        if existing_areas != len(value):
            raise serializers.ValidationError("One or more research area IDs are invalid")

        return value

    def validate_selected_labs(self, value):
        """Validate that lab IDs exist and max 2 labs selected"""
        if len(value) > 2:
            raise serializers.ValidationError("Maximum 2 labs can be selected")

        if len(value) == 0:
            raise serializers.ValidationError("At least 1 lab must be selected")

        # Check if all labs exist
        existing_labs = Lab.objects.filter(id__in=value).count()
        if existing_labs != len(value):
            raise serializers.ValidationError("One or more lab IDs are invalid")

        return value

    def validate_preferred_slots(self, value):
        """Validate time slots format"""
        if len(value) > 3:
            raise serializers.ValidationError("Maximum 3 time slots allowed")

        if len(value) == 0:
            raise serializers.ValidationError("At least 1 time slot must be provided")

        required_fields = {'date', 'time', 'priority'}
        for idx, slot in enumerate(value):
            # Check required fields
            missing_fields = required_fields - set(slot.keys())
            if missing_fields:
                raise serializers.ValidationError(
                    f"Slot {idx + 1}: Missing required fields: {', '.join(missing_fields)}"
                )

            # Validate priority
            priority = slot.get('priority')
            if not isinstance(priority, int) or priority < 1 or priority > 3:
                raise serializers.ValidationError(
                    f"Slot {idx + 1}: Priority must be 1, 2, or 3"
                )

        return value

    def create(self, validated_data):
        """Create session with related research areas, labs and time slots"""
        selected_research_areas = validated_data.pop('selected_research_areas')
        selected_labs = validated_data.pop('selected_labs')
        preferred_slots = validated_data.pop('preferred_slots')

        # Set user from context
        validated_data['user'] = self.context['request'].user

        # Set initial status to pending
        validated_data['status'] = 'pending'

        # Create the session
        session = MockInterviewSession.objects.create(**validated_data)

        # Create research areas
        for idx, research_area_id in enumerate(selected_research_areas):
            SessionResearchArea.objects.create(
                session=session,
                research_area_id=research_area_id,
                priority=idx + 1
            )

        # Create target labs
        for idx, lab_id in enumerate(selected_labs):
            SessionLab.objects.create(
                session=session,
                lab_id=lab_id,
                priority=idx + 1
            )

        # Create preferred time slots
        for slot_data in preferred_slots:
            SessionTimeSlot.objects.create(
                session=session,
                date=slot_data['date'],
                time=slot_data['time'],
                priority=slot_data['priority']
            )

        return session


class SessionStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating session status (admin only)"""
    status = serializers.ChoiceField(choices=MockInterviewSession.STATUS_CHOICES)


class AssignInterviewerSerializer(serializers.Serializer):
    """Serializer for assigning interviewer (admin only)"""
    interviewer_id = serializers.IntegerField()
    match_type = serializers.ChoiceField(choices=MockInterviewSession.MATCH_TYPE_CHOICES)
    confirmed_date = serializers.DateField()
    confirmed_time = serializers.TimeField()

    def validate_interviewer_id(self, value):
        """Validate that interviewer exists"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Interviewer user does not exist")
        return value


class InterviewReviewSerializer(serializers.ModelSerializer):
    """Serializer for interview reviews"""
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    reviewer_type_display = serializers.CharField(source='get_reviewer_type_display', read_only=True)
    session_id = serializers.IntegerField(source='session.id', read_only=True)

    class Meta:
        model = InterviewReview
        fields = [
            'id', 'session', 'session_id', 'reviewer', 'reviewer_name',
            'reviewer_type', 'reviewer_type_display', 'rating', 'comment',
            'communication_rating', 'preparation_rating', 'helpfulness_rating',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reviewer', 'session']

    def validate_rating(self, value):
        """Validate rating is between 1-5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_communication_rating(self, value):
        """Validate communication rating if provided"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Communication rating must be between 1 and 5")
        return value

    def validate_preparation_rating(self, value):
        """Validate preparation rating if provided"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Preparation rating must be between 1 and 5")
        return value

    def validate_helpfulness_rating(self, value):
        """Validate helpfulness rating if provided"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Helpfulness rating must be between 1 and 5")
        return value


class InterviewReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating interview reviews"""

    class Meta:
        model = InterviewReview
        fields = [
            'rating', 'comment', 'communication_rating',
            'preparation_rating', 'helpfulness_rating'
        ]

    def validate_rating(self, value):
        """Validate rating is between 1-5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def create(self, validated_data):
        """Create review with session and reviewer from context"""
        validated_data['session'] = self.context['session']
        validated_data['reviewer'] = self.context['reviewer']
        validated_data['reviewer_type'] = self.context['reviewer_type']
        return super().create(validated_data)
