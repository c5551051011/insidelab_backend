

# apps/authentication/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
#from .views import RegisterView, CustomTokenObtainPairView, verify_email

urlpatterns = [
#    path('register/', RegisterView.as_view(), name='register'),
#    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
#    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#    path('verify-email/', verify_email, name='verify_email'),
]

