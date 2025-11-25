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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserSerializer, RegisterSerializer, UserLabInterestSerializer,
    UserLabInterestCreateSerializer, UserResearchProfileSerializer
)
from .models import UserLabInterest, UserResearchProfile
from .utils import send_verification_email, verify_email_token
from .utils import resend_verification_email as resend_email_util
from .utils import send_feedback_email
from .university_verification import UniversityEmailVerification
from .swagger_schemas import (
    register_request_body, register_response, error_response, success_response,
    login_request_body, login_response, google_auth_request, feedback_request
)

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

    @swagger_auto_schema(
        operation_summary="사용자 회원가입",
        operation_description="새로운 사용자를 등록하고 이메일 인증을 발송합니다.",
        request_body=register_request_body,
        responses={
            201: register_response,
            400: error_response,
            500: error_response
        },
        tags=['Authentication']
    )
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

    @swagger_auto_schema(
        operation_summary="사용자 로그인",
        operation_description="이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.",
        request_body=login_request_body,
        responses={
            200: login_response,
            401: error_response,
            404: error_response
        },
        tags=['Authentication']
    )
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

    # Get language from query parameter
    language = request.GET.get('lang', 'ko')  # Default to Korean

    user = verify_email_token(token)

    if user:
        # Determine messages based on language
        if language == 'en':
            message = 'Email verification completed successfully!'
            template = 'verification/success_en.html'
        else:
            message = '이메일 인증이 완료되었습니다!'
            template = 'verification/success.html'

        return render(request, template, {
            'user': user,
            'message': message,
            'success': True,
            'language': language
        })
    else:
        # Determine error messages based on language
        if language == 'en':
            error_message = 'Invalid or expired verification token.'
            template = 'verification/error_en.html'
        else:
            error_message = '잘못되었거나 만료된 인증 토큰입니다.'
            template = 'verification/error.html'

        return render(request, template, {
            'error_message': error_message,
            'success': False,
            'language': language
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
    # Get language from query parameter
    language = request.GET.get('lang', 'ko')  # Default to Korean

    try:
        user = User.objects.get(id=user_id)
        # Here you might set an unsubscribe flag if you add one to the model

        # Determine messages based on language
        if language == 'en':
            message = 'Successfully unsubscribed from emails.'
        else:
            message = '구독 취소가 완료되었습니다.'

        return Response({
            'message': message,
            'success': True,
            'language': language
        })
    except User.DoesNotExist:
        # Determine error messages based on language
        if language == 'en':
            error_message = 'User not found.'
        else:
            error_message = '사용자를 찾을 수 없습니다.'

        return Response({
            'error': error_message,
            'success': False,
            'language': language
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


@swagger_auto_schema(
    method='post',
    operation_summary="Google OAuth 로그인",
    operation_description="Google 계정으로 로그인하거나 신규 가입합니다.",
    request_body=google_auth_request,
    responses={
        200: login_response,
        400: error_response
    },
    tags=['Authentication']
)
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
            'lab', 'lab__head_professor', 'lab__university_department__university',
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


# University Email Verification Endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_university_verification(request):
    """Send university email verification (like Blind)"""
    university_email = request.data.get('university_email')

    if not university_email:
        return Response({
            'error': 'University email is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if email domain is supported
    if not UniversityEmailVerification.is_university_email(university_email):
        return Response({
            'error': 'This email domain is not supported. Please contact support to add your university.',
            'can_request_domain': True
        }, status=status.HTTP_400_BAD_REQUEST)

    # Send verification email
    success, message = UniversityEmailVerification.send_university_verification_email(
        request.user, university_email, request
    )

    if success:
        return Response({
            'message': message,
            'university_email': university_email,
            'university': UniversityEmailVerification.get_university_by_email(university_email).name
        })
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_university_email(request, token):
    """Verify university email using token"""
    success, result = UniversityEmailVerification.verify_university_email_token(token)

    if success:
        user = result
        return Response({
            'message': 'University email verified successfully!',
            'university': user.verified_university.name if user.verified_university else None,
            'verified_email': user.university_email
        })
    else:
        return Response({
            'error': result
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_university_verification(request):
    """Resend university verification email"""
    success, message = UniversityEmailVerification.resend_university_verification(request.user)

    if success:
        return Response({'message': message})
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_university_domain(request):
    """Request addition of new university domain"""
    university_email = request.data.get('university_email')
    university_name = request.data.get('university_name')
    notes = request.data.get('notes', '')

    if not university_email or not university_name:
        return Response({
            'error': 'University email and name are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    success, message = UniversityEmailVerification.request_new_university_domain(
        university_email, university_name, request.user.display_name, notes
    )

    if success:
        return Response({'message': message})
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_university_email(request):
    """Check if email domain is supported (public endpoint)"""
    email = request.data.get('email')

    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    is_supported = UniversityEmailVerification.is_university_email(email)
    university = UniversityEmailVerification.get_university_by_email(email)

    return Response({
        'is_supported': is_supported,
        'university': university.name if university else None,
        'can_verify': is_supported
    })


@swagger_auto_schema(
    method='post',
    operation_summary="이메일 중복 확인",
    operation_description="회원가입 시 이메일 중복 여부를 확인합니다.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='확인할 이메일 주소')
        }
    ),
    responses={
        200: openapi.Response(
            description='중복 확인 결과',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'available': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='사용 가능 여부'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='결과 메시지')
                }
            )
        ),
        400: error_response
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_availability(request):
    """Check if email is already registered"""
    email = request.data.get('email')

    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return Response({
            'error': 'Invalid email format'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if email exists
    email_exists = User.objects.filter(email=email).exists()

    return Response({
        'available': not email_exists,
        'message': 'Email is available' if not email_exists else 'Email is already registered'
    })


@swagger_auto_schema(
    method='post',
    operation_summary="사용자명 중복 확인",
    operation_description="회원가입 시 사용자명(username) 중복 여부를 확인합니다.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='확인할 사용자명')
        }
    ),
    responses={
        200: openapi.Response(
            description='중복 확인 결과',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'available': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='사용 가능 여부'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='결과 메시지')
                }
            )
        ),
        400: error_response
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_username_availability(request):
    """Check if username is already taken"""
    username = request.data.get('username')

    if not username:
        return Response({
            'error': 'Username is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate username format (alphanumeric and underscore only)
    import re
    username_pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(username_pattern, username):
        return Response({
            'error': 'Username can only contain letters, numbers, and underscores'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check minimum length
    if len(username) < 3:
        return Response({
            'error': 'Username must be at least 3 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if username exists
    username_exists = User.objects.filter(username=username).exists()

    return Response({
        'available': not username_exists,
        'message': 'Username is available' if not username_exists else 'Username is already taken'
    })


@swagger_auto_schema(
    method='post',
    operation_summary="피드백 전송",
    operation_description="InsideLab 팀에 문의사항이나 피드백을 전송합니다.",
    request_body=feedback_request,
    responses={
        200: success_response,
        400: error_response,
        500: error_response
    },
    tags=['Feedback']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_feedback(request):
    """Send feedback email to InsideLab team"""
    user_email = request.data.get('email')
    user_name = request.data.get('name', '')
    subject = request.data.get('subject')
    message = request.data.get('message')

    # Validate required fields
    if not user_email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not subject:
        return Response({
            'error': 'Subject is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not message:
        return Response({
            'error': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, user_email):
        return Response({
            'error': 'Invalid email format'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Determine user type (authenticated vs anonymous)
    user_type = "authenticated" if request.user.is_authenticated else "anonymous"
    if request.user.is_authenticated:
        # Use authenticated user's info if different from provided
        actual_name = request.user.name or user_name
        actual_email = request.user.email
    else:
        actual_name = user_name
        actual_email = user_email

    # Send feedback email
    try:
        success = send_feedback_email(
            user_email=actual_email,
            user_name=actual_name,
            subject=subject,
            message=message,
            user_type=user_type
        )

        if success:
            return Response({
                'message': 'Feedback sent successfully. Thank you for your input!',
                'success': True
            })
        else:
            return Response({
                'error': 'Failed to send feedback. Please try again later.',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'error': 'An error occurred while sending feedback',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserResearchProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user research profiles"""
    serializer_class = UserResearchProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return the current user's research profile
        return UserResearchProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure only one profile per user
        existing_profile = UserResearchProfile.objects.filter(user=self.request.user).first()
        if existing_profile:
            # Update existing profile instead of creating new one
            for attr, value in serializer.validated_data.items():
                setattr(existing_profile, attr, value)
            existing_profile.save()
            serializer.instance = existing_profile
        else:
            serializer.save(user=self.request.user)
