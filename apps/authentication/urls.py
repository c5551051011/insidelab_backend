

# apps/authentication/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomTokenObtainPairView, verify_email,
    get_current_user, update_profile, google_auth, resend_verification_email,
    unsubscribe, test_registration, UserLabInterestViewSet, UserResearchProfileViewSet,
    send_university_verification, verify_university_email, resend_university_verification,
    request_university_domain, check_university_email, send_feedback,
    check_email_availability, check_username_availability
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'lab-interests', UserLabInterestViewSet, basename='user-lab-interests')
router.register(r'research-profile', UserResearchProfileViewSet, basename='user-research-profile')

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

    # Duplicate check endpoints
    path('check-email/', check_email_availability, name='check_email_availability'),
    path('check-username/', check_username_availability, name='check_username_availability'),

    # University email verification endpoints
    path('university/send-verification/', send_university_verification, name='send_university_verification'),
    path('university/verify/<str:token>/', verify_university_email, name='verify_university_email'),
    path('university/resend-verification/', resend_university_verification, name='resend_university_verification'),
    path('university/request-domain/', request_university_domain, name='request_university_domain'),
    path('university/check-email/', check_university_email, name='check_university_email'),

    # Feedback endpoint
    path('feedback/', send_feedback, name='send_feedback'),

    # Include ViewSet URLs
    path('', include(router.urls)),
]

