# apps/interviews/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from .models import MockInterviewSession
from .serializers import (
    MockInterviewSessionListSerializer,
    MockInterviewSessionDetailSerializer,
    MockInterviewSessionCreateSerializer,
    SessionStatusUpdateSerializer,
    AssignInterviewerSerializer
)



class InterviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mock interview sessions.

    - list: Get all sessions for the current user
    - create: Book a new mock interview session
    - retrieve: Get details of a specific session
    - update/partial_update: Not allowed for users (admin only)
    - destroy: Not allowed

    Admin-only actions:
    - assign_interviewer: Assign interviewer to a session
    - update_status: Update session status
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own sessions"""
        user = self.request.user

        queryset = MockInterviewSession.objects.filter(user=user).select_related(
            'user', 'interviewer'
        ).prefetch_related(
            'target_labs__lab__university',
            'target_labs__lab__department',
            'target_labs__lab__field',
            'target_labs__lab__professor',
            'preferred_slots'
        )

        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return MockInterviewSessionListSerializer
        elif self.action == 'create':
            return MockInterviewSessionCreateSerializer
        else:
            return MockInterviewSessionDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new mock interview session booking"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()

        # Return detailed response
        response_serializer = MockInterviewSessionDetailSerializer(session)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Users cannot update sessions directly"""
        return Response(
            {'error': 'Direct updates not allowed. Use cancel action or contact admin.'},
            status=status.HTTP_403_FORBIDDEN
        )

    def partial_update(self, request, *args, **kwargs):
        """Users cannot update sessions directly"""
        return Response(
            {'error': 'Direct updates not allowed. Use cancel action or contact admin.'},
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        """Users cannot delete sessions, only cancel them"""
        return Response(
            {'error': 'Cannot delete sessions. Use cancel action instead.'},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a session (user action)"""
        session = self.get_object()

        # Only allow cancellation if not already cancelled or completed
        if session.status in ['cancelled', 'completed']:
            return Response(
                {'error': f'Cannot cancel a {session.status} session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = 'cancelled'
        session.save()

        serializer = MockInterviewSessionDetailSerializer(session)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming sessions (confirmed but not completed)"""
        sessions = self.get_queryset().filter(
            status__in=['pending', 'matching', 'confirmed']
        ).order_by('confirmed_date', 'confirmed_time')

        page = self.paginate_queryset(sessions)
        if page is not None:
            serializer = MockInterviewSessionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MockInterviewSessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past sessions (completed or cancelled)"""
        sessions = self.get_queryset().filter(
            status__in=['completed', 'cancelled']
        ).order_by('-confirmed_date', '-confirmed_time')

        page = self.paginate_queryset(sessions)
        if page is not None:
            serializer = MockInterviewSessionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MockInterviewSessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    # Admin-only actions
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_interviewer(self, request, pk=None):
        """
        Assign an interviewer to a session (admin only)

        Required fields:
        - interviewer_id: User ID of the interviewer
        - match_type: Type of match (exact-lab, same-department, same-field)
        - confirmed_date: Confirmed session date
        - confirmed_time: Confirmed session time
        """
        session = get_object_or_404(MockInterviewSession, pk=pk)

        serializer = AssignInterviewerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session.interviewer_id = serializer.validated_data['interviewer_id']
        session.match_type = serializer.validated_data['match_type']
        session.confirmed_date = serializer.validated_data['confirmed_date']
        session.confirmed_time = serializer.validated_data['confirmed_time']
        session.status = 'confirmed'
        session.save()

        response_serializer = MockInterviewSessionDetailSerializer(session)
        return Response(response_serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """
        Update session status (admin only)

        Required field:
        - status: New status value
        """
        session = get_object_or_404(MockInterviewSession, pk=pk)

        serializer = SessionStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session.status = serializer.validated_data['status']
        session.save()

        response_serializer = MockInterviewSessionDetailSerializer(session)
        return Response(response_serializer.data)
