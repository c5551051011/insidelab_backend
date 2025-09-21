

# apps/authentication/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomTokenObtainPairView, verify_email,
    get_current_user, update_profile, google_auth, resend_verification_email, unsubscribe, test_registration
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('test-register/', test_registration, name='test_registration'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/<str:token>/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification_email'),
    path('unsubscribe/<int:user_id>/', unsubscribe, name='unsubscribe'),
    path('user/', get_current_user, name='get_current_user'),
    path('profile/', update_profile, name='update_profile'),
    path('google/', google_auth, name='google_auth'),
]

