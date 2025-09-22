# apps/authentication/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
import uuid
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user, request=None):
    """
    Send email verification email to user

    Args:
        user: User instance
        request: HttpRequest instance (optional, for getting domain)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Generate verification token
        verification_token = str(uuid.uuid4())
        user.email_verification_token = verification_token
        user.email_verification_sent_at = timezone.now()
        user.save()

        # Get domain - robust method that works in production
        if request:
            try:
                # Try to get host from request headers first
                host = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
                domain = host

                # Force Railway domain for production
                if 'railway' in host or 'localhost' not in host:
                    domain = 'insidelab.up.railway.app'
                    protocol = 'https'
            except Exception:
                # Fallback for production environment
                domain = 'insidelab.up.railway.app'
                protocol = 'https'
        else:
            # Default for production deployment
            domain = 'insidelab.up.railway.app'
            protocol = 'https'

        # Generate URLs
        verification_url = f"{protocol}://{domain}{reverse('verify_email', kwargs={'token': verification_token})}"
        unsubscribe_url = f"{protocol}://{domain}{reverse('unsubscribe', kwargs={'user_id': user.id})}"

        # Email context
        context = {
            'user_name': user.name or user.email.split('@')[0],
            'verification_url': verification_url,
            'unsubscribe_url': unsubscribe_url,
            'domain': domain,
        }

        # Render templates
        html_content = render_to_string('emails/verification.html', context)
        text_content = render_to_string('emails/verification.txt', context)

        # Email subject
        subject = '🔬 InsideLab 이메일 인증을 완료해 주세요'

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'InsideLab <noreply@insidelab.com>'),
            to=[user.email]
        )

        # Attach HTML version
        email.attach_alternative(html_content, "text/html")

        # Send email to user
        email.send()

        logger.info(f"Verification email sent successfully to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def verify_email_token(token):
    """
    Verify email verification token

    Args:
        token: Verification token string

    Returns:
        User instance if valid, None otherwise
    """
    try:
        from .models import User

        user = User.objects.get(email_verification_token=token)

        # Check if token is not expired (24 hours)
        if user.email_verification_sent_at:
            time_diff = timezone.now() - user.email_verification_sent_at
            if time_diff.total_seconds() > 24 * 60 * 60:  # 24 hours
                logger.warning(f"Expired verification token used for {user.email}")
                return None

        # Mark email as verified
        user.email_verified = True
        user.email_verification_token = ''
        user.save()

        logger.info(f"Email verified successfully for {user.email}")
        return user

    except User.DoesNotExist:
        logger.warning(f"Invalid verification token used: {token}")
        return None
    except Exception as e:
        logger.error(f"Error verifying email token: {str(e)}")
        return None


def resend_verification_email(user, request=None):
    """
    Resend verification email with rate limiting

    Args:
        user: User instance
        request: HttpRequest instance (optional)

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check rate limiting (1 email per 5 minutes)
        if user.email_verification_sent_at:
            time_diff = timezone.now() - user.email_verification_sent_at
            if time_diff.total_seconds() < 5 * 60:  # 5 minutes
                remaining = 5 * 60 - time_diff.total_seconds()
                return False, f"이메일 재발송은 {int(remaining/60)}분 후에 가능합니다."

        # Send email
        success = send_verification_email(user, request)

        if success:
            return True, "인증 이메일이 재발송되었습니다."
        else:
            return False, "이메일 발송에 실패했습니다. 잠시 후 다시 시도해 주세요."

    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        return False, "시스템 오류가 발생했습니다."


def is_email_verified(user):
    """
    Check if user's email is verified

    Args:
        user: User instance

    Returns:
        bool: True if email is verified
    """
    return user.email_verified if user else False