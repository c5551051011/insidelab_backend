# apps/interviews/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_date
from .models import MockInterviewSession, InterviewReview
from .serializers import (
    MockInterviewSessionListSerializer,
    MockInterviewSessionDetailSerializer,
    MockInterviewSessionCreateSerializer,
    SessionStatusUpdateSerializer,
    AssignInterviewerSerializer,
    InterviewReviewSerializer,
    InterviewReviewCreateSerializer
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
            'user', 'interviewer', 'research_area'
        ).prefetch_related(
            'research_areas__research_area__department',
            'target_labs__lab__university_department__university',
            'target_labs__lab__university_department__department',
            'target_labs__lab__research_group',
            'target_labs__lab__head_professor',
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

    # =================================================================
    # SERVICE PROVIDER ENDPOINTS
    # =================================================================

    @action(detail=False, methods=['get'])
    def provider_dashboard(self, request):
        """Get provider dashboard overview with performance metrics"""
        user = request.user

        # Get sessions where user is the interviewer
        provider_sessions = MockInterviewSession.objects.filter(interviewer=user)

        # Calculate metrics
        from django.utils import timezone
        from datetime import datetime, timedelta

        now = timezone.now()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # This month bookings
        this_month_bookings = provider_sessions.filter(
            created_at__gte=current_month
        ).count()

        # Average rating (from reviews)
        completed_sessions = provider_sessions.filter(status='completed')
        if hasattr(user, 'professor_profile') and user.professor_profile:
            avg_rating = float(user.professor_profile.overall_rating) if user.professor_profile.overall_rating else 0.0
            review_count = user.professor_profile.review_count
        else:
            avg_rating = 0.0
            review_count = 0

        # Total earnings
        total_earnings = sum(
            float(session.total_price)
            for session in completed_sessions
            if session.total_price
        )

        # Completed services
        completed_services = completed_sessions.count()

        # Upcoming sessions
        upcoming_sessions = provider_sessions.filter(
            status__in=['confirmed'],
            confirmed_date__gte=timezone.now().date()
        ).order_by('confirmed_date', 'confirmed_time')[:10]

        # Pending requests
        pending_requests = provider_sessions.filter(
            status__in=['pending', 'matching']
        ).order_by('-created_at')[:5]

        return Response({
            'performance_overview': {
                'this_month_bookings': this_month_bookings,
                'average_rating': round(avg_rating, 1),
                'total_earnings': total_earnings,
                'completed_services': completed_services
            },
            'upcoming_sessions': MockInterviewSessionListSerializer(upcoming_sessions, many=True).data,
            'pending_requests': MockInterviewSessionListSerializer(pending_requests, many=True).data
        })

    @action(detail=False, methods=['get'])
    def provider_sessions(self, request):
        """Get all sessions for the provider (interviewer)"""
        user = request.user
        status_filter = request.query_params.get('status', None)

        sessions = MockInterviewSession.objects.filter(interviewer=user)

        if status_filter:
            sessions = sessions.filter(status=status_filter)

        sessions = sessions.order_by('-created_at')

        page = self.paginate_queryset(sessions)
        if page is not None:
            serializer = MockInterviewSessionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MockInterviewSessionListSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def provider_earnings(self, request):
        """Get detailed earnings report for provider"""
        user = request.user

        # Filter by date range if provided
        from django.utils.dateparse import parse_date
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        sessions = MockInterviewSession.objects.filter(
            interviewer=user,
            status='completed'
        )

        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                sessions = sessions.filter(completed_at__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                sessions = sessions.filter(completed_at__lte=end_date)

        # Calculate earnings by month
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth

        monthly_earnings = sessions.annotate(
            month=TruncMonth('completed_at')
        ).values('month').annotate(
            total_earnings=Sum('total_price'),
            session_count=models.Count('id')
        ).order_by('-month')

        # Total earnings
        total_earnings = sessions.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        # Session breakdown
        session_types = sessions.values('session_type').annotate(
            count=models.Count('id'),
            earnings=Sum('total_price')
        )

        return Response({
            'total_earnings': float(total_earnings),
            'total_sessions': sessions.count(),
            'monthly_earnings': [
                {
                    'month': item['month'].strftime('%Y-%m'),
                    'earnings': float(item['total_earnings']),
                    'session_count': item['session_count']
                }
                for item in monthly_earnings
            ],
            'session_type_breakdown': [
                {
                    'type': item['session_type'],
                    'count': item['count'],
                    'earnings': float(item['earnings'] or 0)
                }
                for item in session_types
            ]
        })

    @action(detail=False, methods=['get'])
    def provider_reviews(self, request):
        """Get interview-specific reviews for provider"""
        user = request.user

        # Get interview reviews where this user was the interviewer
        reviews = InterviewReview.objects.filter(
            session__interviewer=user,
            reviewer_type='interviewee',  # Reviews from interviewees about the interviewer
            is_active=True
        ).select_related('session', 'reviewer').order_by('-created_at')

        # Filter by recent if requested
        recent_only = request.query_params.get('recent', 'false').lower() == 'true'
        if recent_only:
            reviews = reviews[:10]

        # Calculate statistics
        total_reviews = reviews.count()
        if total_reviews > 0:
            avg_rating = reviews.aggregate(
                avg=models.Avg('rating')
            )['avg']
            avg_communication = reviews.filter(
                communication_rating__isnull=False
            ).aggregate(avg=models.Avg('communication_rating'))['avg']
            avg_preparation = reviews.filter(
                preparation_rating__isnull=False
            ).aggregate(avg=models.Avg('preparation_rating'))['avg']
            avg_helpfulness = reviews.filter(
                helpfulness_rating__isnull=False
            ).aggregate(avg=models.Avg('helpfulness_rating'))['avg']
        else:
            avg_rating = 0.0
            avg_communication = 0.0
            avg_preparation = 0.0
            avg_helpfulness = 0.0

        # Serialize reviews
        serializer = InterviewReviewSerializer(reviews, many=True)

        return Response({
            'reviews': serializer.data,
            'statistics': {
                'total_reviews': total_reviews,
                'average_rating': round(float(avg_rating or 0), 1),
                'average_communication': round(float(avg_communication or 0), 1),
                'average_preparation': round(float(avg_preparation or 0), 1),
                'average_helpfulness': round(float(avg_helpfulness or 0), 1)
            }
        })

    @action(detail=True, methods=['post'])
    def accept_request(self, request, pk=None):
        """Accept a pending interview request"""
        session = self.get_object()

        # Verify user can accept this request
        if session.interviewer != request.user:
            return Response(
                {'error': 'You are not authorized to accept this request'},
                status=status.HTTP_403_FORBIDDEN
            )

        if session.status not in ['pending', 'matching']:
            return Response(
                {'error': 'Session cannot be accepted in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update session status
        session.status = 'confirmed'
        session.match_type = request.data.get('match_type', 'exact-lab')
        session.confirmed_date = request.data.get('confirmed_date')
        session.confirmed_time = request.data.get('confirmed_time')
        session.zoom_link = request.data.get('zoom_link', '')
        session.save()

        serializer = MockInterviewSessionDetailSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def decline_request(self, request, pk=None):
        """Decline a pending interview request"""
        session = self.get_object()

        # Verify user can decline this request
        if session.interviewer != request.user:
            return Response(
                {'error': 'You are not authorized to decline this request'},
                status=status.HTTP_403_FORBIDDEN
            )

        if session.status not in ['pending', 'matching']:
            return Response(
                {'error': 'Session cannot be declined in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update session status
        session.status = 'cancelled'
        session.additional_notes = f"Declined by interviewer. Reason: {request.data.get('reason', 'No reason provided')}"
        session.save()

        serializer = MockInterviewSessionDetailSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_review(self, request, pk=None):
        """Create a review for a completed interview session"""
        session = self.get_object()
        user = request.user

        # Verify session is completed
        if session.status != 'completed':
            return Response(
                {'error': 'Reviews can only be created for completed sessions'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determine reviewer type
        if user == session.user:
            reviewer_type = 'interviewee'
        elif user == session.interviewer:
            reviewer_type = 'interviewer'
        else:
            return Response(
                {'error': 'You are not authorized to review this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if user already reviewed this session
        existing_review = InterviewReview.objects.filter(
            session=session,
            reviewer=user,
            reviewer_type=reviewer_type
        ).first()

        if existing_review:
            return Response(
                {'error': 'You have already reviewed this session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create review
        serializer = InterviewReviewCreateSerializer(
            data=request.data,
            context={
                'session': session,
                'reviewer': user,
                'reviewer_type': reviewer_type
            }
        )

        if serializer.is_valid():
            review = serializer.save()
            response_serializer = InterviewReviewSerializer(review)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific interview session"""
        session = self.get_object()
        user = request.user

        # Only allow session participants to view reviews
        if user not in [session.user, session.interviewer]:
            return Response(
                {'error': 'You are not authorized to view reviews for this session'},
                status=status.HTTP_403_FORBIDDEN
            )

        reviews = InterviewReview.objects.filter(
            session=session,
            is_active=True
        ).order_by('-created_at')

        serializer = InterviewReviewSerializer(reviews, many=True)
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
