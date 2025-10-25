# apps/authentication/authentication.py
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication with enhanced logging for debugging"""

    def authenticate(self, request):
        try:
            header = self.get_header(request)
            if header is None:
                return None

            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)

            logger.info(f"JWT authentication successful for user: {user.email}")
            return (user, validated_token)

        except TokenError as e:
            logger.warning(f"JWT authentication failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            return None

    def get_user(self, validated_token):
        """Get user from validated token with error handling"""
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken('Token contained no recognizable user identification')

            try:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    raise InvalidToken('User account is disabled')
                return user
            except User.DoesNotExist:
                raise InvalidToken('User not found')

        except Exception as e:
            logger.error(f"Error getting user from token: {str(e)}")
            raise InvalidToken('Invalid token')