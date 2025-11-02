# apps/interviews/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MockInterviewSession, SessionLab, SessionTimeSlot, SessionResearchArea
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

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'position', 'university', 'department']


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

    class Meta:
        model = MockInterviewSession
        fields = [
            'id', 'session_type', 'session_type_display', 'status', 'status_display',
            'confirmed_date', 'confirmed_time', 'total_price',
            'interviewer_email', 'match_type', 'created_at', 'updated_at',
            'research_area_count', 'target_lab_count', 'preferred_slot_count',
            'primary_research_area', 'primary_lab',
            'research_area_names', 'target_lab_names', 'preferred_slot_summary'
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
                'university': lab.lab.university.name if lab.lab.university else '',
                'priority': lab.priority
            }
            for lab in obj.target_labs.all().order_by('priority')
        ]

    def get_preferred_slot_summary(self, obj):
        """Get summary of preferred time slots"""
        return [
            {
                'date': slot.date.strftime('%Y-%m-%d'),
                'time': slot.time.strftime('%H:%M'),
                'priority': slot.priority
            }
            for slot in obj.preferred_slots.all().order_by('priority')
        ]


class MockInterviewSessionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed session view"""
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    match_type_display = serializers.CharField(source='get_match_type_display', read_only=True, allow_null=True)

    research_areas = SessionResearchAreaSerializer(many=True, read_only=True)
    target_labs = SessionLabSerializer(many=True, read_only=True)
    preferred_slots = SessionTimeSlotSerializer(many=True, read_only=True)
    interviewer = InterviewerSerializer(read_only=True)

    class Meta:
        model = MockInterviewSession
        fields = [
            'id', 'session_type', 'session_type_display', 'status', 'status_display',
            'focus_areas', 'additional_notes', 'match_type', 'match_type_display',
            'interviewer', 'confirmed_date', 'confirmed_time', 'total_price',
            'research_areas', 'target_labs', 'preferred_slots', 'created_at', 'updated_at'
        ]


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
