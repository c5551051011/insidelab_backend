# apps/authentication/views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer

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
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            response.data = {
                'message': 'User registered successfully. Please check your email for verification.',
                'user': response.data
            }
        return response


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


@api_view(['POST'])
def verify_email(request):
    token = request.data.get('token')
    try:
        user = User.objects.get(verification_token=token)
        user.is_verified = True
        user.verification_status = 'verified'
        user.verification_token = ''
        user.save()
        return Response({
            'message': 'Email verified successfully',
            'user': UserSerializer(user).data
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid verification token'},
            status=status.HTTP_400_BAD_REQUEST
        )


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
