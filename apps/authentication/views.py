# apps/authentication/views.py
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from .serializers import (
    UserSerializer, RegisterSerializer, UserLabInterestSerializer,
    UserLabInterestCreateSerializer
)
from .models import UserLabInterest
from .utils import send_verification_email, verify_email_token
from .utils import resend_verification_email as resend_email_util

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['name'] = user.name
        
        return token

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Create user within transaction
                response = super().create(request, *args, **kwargs)

                if response.status_code == 201:
                    user_id = response.data.get('id')
                    user = User.objects.get(id=user_id)

                    # Send verification email - if this fails, rollback user creation
                    email_sent = send_verification_email(user, request)

                    if not email_sent:
                        # Force transaction rollback by raising exception
                        raise Exception("Failed to send verification email")

                    response.data = {
                        'message': 'User registered successfully. Please check your email for verification.',
                        'user': response.data,
                        'email_sent': email_sent
                    }

                return response

        except Exception as e:
            print(f"Registration error: {str(e)}")
            from rest_framework.response import Response
            from rest_framework import status

            # Return appropriate error message based on failure type
            if "verification email" in str(e).lower():
                return Response({
                    'error': 'Registration failed: Unable to send verification email. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': f'Registration failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            # Check if user exists with provided email
            email = request.data.get('email')
            if email:
                user = User.objects.get(email=email)
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                user_data = UserSerializer(user).data
                response.data['user'] = user_data
                
        except User.DoesNotExist:
            return Response(
                {'error': 'No account found with this email address'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        return response


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    """Verify email using token from URL"""
    from django.shortcuts import render

    user = verify_email_token(token)

    if user:
        return render(request, 'verification/success.html', {
            'user': user,
            'message': '이메일 인증이 완료되었습니다!',
            'success': True
        })
    else:
        return render(request, 'verification/error.html', {
            'error_message': '잘못되었거나 만료된 인증 토큰입니다.',
            'success': False
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """Resend verification email"""
    email = request.data.get('email')

    if not email:
        return Response({
            'error': '이메일 주소가 필요합니다.',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)

        if user.email_verified:
            return Response({
                'error': '이미 인증된 이메일입니다.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        success, message = resend_email_util(user, request)

        return Response({
            'message': message,
            'success': success
        }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({
            'error': '해당 이메일로 등록된 계정이 없습니다.',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def unsubscribe(request, user_id):
    """Unsubscribe user from emails"""
    try:
        user = User.objects.get(id=user_id)
        # Here you might set an unsubscribe flag if you add one to the model
        return Response({
            'message': '구독 취소가 완료되었습니다.',
            'success': True
        })
    except User.DoesNotExist:
        return Response({
            'error': '사용자를 찾을 수 없습니다.',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user data"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_registration(request):
    """Simple test endpoint to debug registration issues"""
    try:
        return Response({
            'message': 'Test endpoint working',
            'received_data': request.data
        })
    except Exception as e:
        return Response({
            'error': f'Test failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """Handle Google authentication"""
    id_token = request.data.get('id_token')
    email = request.data.get('email')
    name = request.data.get('name')

    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Try to get existing user
        user = User.objects.get(email=email)

        # Update user info if provided
        if name and not user.name:
            user.name = name
            user.save()

    except User.DoesNotExist:
        # Create new user
        username = email.split('@')[0]
        # Ensure unique username
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            email=email,
            username=username,
            name=name or email.split('@')[0],
            is_verified=True,  # Google accounts are pre-verified
            verification_status='verified'
        )

    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    # Add custom claims
    access_token['email'] = user.email
    access_token['username'] = user.username
    access_token['name'] = user.name

    return Response({
        'access': str(access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })


class UserLabInterestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user lab interests"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own lab interests
        return UserLabInterest.objects.filter(user=self.request.user).select_related(
            'lab', 'lab__professor', 'lab__university_department__university',
            'lab__university_department__department'
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return UserLabInterestCreateSerializer
        return UserLabInterestSerializer

    def perform_create(self, serializer):
        # Auto-assign the current user
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of user's lab interests"""
        interests = self.get_queryset()

        # Group by interest type
        summary = {}
        for interest in interests:
            interest_type = interest.interest_type
            if interest_type not in summary:
                summary[interest_type] = []

            summary[interest_type].append({
                'id': interest.id,
                'lab_id': interest.lab.id,
                'lab_name': interest.lab.name,
                'lab_professor': interest.lab.professor.name,
                'lab_rating': float(interest.lab.overall_rating),
                'created_at': interest.created_at
            })

        return Response({
            'total_interests': interests.count(),
            'by_type': summary,
            'interest_types': [
                {'value': 'general', 'label': 'General Interest'},
                {'value': 'application', 'label': 'Considering Application'},
                {'value': 'watching', 'label': 'Watching for Updates'},
                {'value': 'recruited', 'label': 'Applied/Recruited'},
            ]
        })

    @action(detail=False, methods=['post'])
    def toggle_interest(self, request):
        """Toggle interest in a lab (add if not exists, remove if exists)"""
        lab_id = request.data.get('lab_id')
        interest_type = request.data.get('interest_type', 'general')

        if not lab_id:
            return Response(
                {'error': 'lab_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.labs.models import Lab
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            return Response(
                {'error': 'Lab not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if interest already exists
        interest, created = UserLabInterest.objects.get_or_create(
            user=request.user,
            lab=lab,
            defaults={
                'interest_type': interest_type,
                'notes': request.data.get('notes', '')
            }
        )

        if created:
            serializer = UserLabInterestSerializer(interest)
            return Response({
                'action': 'added',
                'interest': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            # Update existing interest
            interest.interest_type = interest_type
            interest.notes = request.data.get('notes', interest.notes)
            interest.save()

            serializer = UserLabInterestSerializer(interest)
            return Response({
                'action': 'updated',
                'interest': serializer.data
            })

    @action(detail=False, methods=['delete'])
    def remove_interest(self, request):
        """Remove interest in a lab"""
        lab_id = request.query_params.get('lab_id')

        if not lab_id:
            return Response(
                {'error': 'lab_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            interest = UserLabInterest.objects.get(
                user=request.user,
                lab_id=lab_id
            )
            interest.delete()
            return Response({
                'action': 'removed',
                'message': 'Lab interest removed successfully'
            })
        except UserLabInterest.DoesNotExist:
            return Response(
                {'error': 'Interest not found'},
                status=status.HTTP_404_NOT_FOUND
            )
