# apps/authentication/university_verification.py
import secrets
import logging
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from apps.universities.models import UniversityEmailDomain

logger = logging.getLogger(__name__)


class UniversityEmailVerification:
    """University email verification system like Blind"""

    @staticmethod
    def is_university_email(email):
        """Check if email domain is a registered university domain"""
        return UniversityEmailDomain.is_university_email(email)

    @staticmethod
    def get_university_by_email(email):
        """Get university by email domain"""
        return UniversityEmailDomain.get_university_by_email(email)

    @staticmethod
    def generate_verification_token():
        """Generate secure verification token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def send_university_verification_email(user, university_email, request=None):
        """Send verification email to university address"""
        try:
            # Check if email domain is supported
            if not UniversityEmailVerification.is_university_email(university_email):
                return False, "This email domain is not supported. Please contact support to add your university."

            # Generate verification token
            verification_token = UniversityEmailVerification.generate_verification_token()

            # Update user record
            user.university_email = university_email
            user.university_email_verification_token = verification_token
            user.university_email_verification_sent_at = timezone.now()
            user.university_email_verified = False
            user.save()

            # Get university for email template
            university = UniversityEmailVerification.get_university_by_email(university_email)

            # Create verification URL
            if request:
                verification_url = request.build_absolute_uri(
                    reverse('verify_university_email', kwargs={'token': verification_token})
                )
            else:
                verification_url = f"{settings.FRONTEND_URL}/verify-university-email/{verification_token}"

            # Email subject and content
            subject = f"[InsideLab] Verify your {university.name if university else 'university'} email"

            # HTML email template
            html_message = render_to_string('emails/university_verification.html', {
                'user': user,
                'university': university,
                'university_email': university_email,
                'verification_url': verification_url,
                'token': verification_token,
                'expires_hours': 24,
            })

            # Plain text fallback
            plain_message = f"""
Hello,

You've requested to verify your university email address for InsideLab.

University: {university.name if university else 'Unknown'}
Email: {university_email}

Please click the link below to verify your email:
{verification_url}

This verification link will expire in 24 hours.

If you didn't request this verification, please ignore this email.

Best regards,
InsideLab Team
            """.strip()

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[university_email],
                fail_silently=False,
            )

            logger.info(f"University verification email sent to {university_email} for user {user.id}")
            return True, "Verification email sent successfully"

        except Exception as e:
            logger.error(f"Failed to send university verification email: {str(e)}")
            return False, f"Failed to send verification email: {str(e)}"

    @staticmethod
    def verify_university_email_token(token):
        """Verify university email using token"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Find user with this token
            user = User.objects.get(
                university_email_verification_token=token,
                university_email_verified=False,
                university_email__isnull=False
            )

            # Check if token is expired (24 hours)
            if user.university_email_verification_sent_at:
                expiry_time = user.university_email_verification_sent_at + timedelta(hours=24)
                if timezone.now() > expiry_time:
                    return False, "Verification token has expired. Please request a new one."

            # Get university from email domain
            university = UniversityEmailVerification.get_university_by_email(user.university_email)

            # Mark as verified
            user.university_email_verified = True
            user.verified_university = university
            user.university_email_verification_token = ''  # Clear token for security
            user.save()

            logger.info(f"University email verified for user {user.id}: {user.university_email}")
            return True, user

        except User.DoesNotExist:
            return False, "Invalid or expired verification token"
        except Exception as e:
            logger.error(f"University email verification failed: {str(e)}")
            return False, f"Verification failed: {str(e)}"

    @staticmethod
    def resend_university_verification(user):
        """Resend university verification email"""
        if not user.university_email:
            return False, "No university email found for this user"

        if user.university_email_verified:
            return False, "University email is already verified"

        # Check rate limiting (don't send more than once per 5 minutes)
        if user.university_email_verification_sent_at:
            time_since_last = timezone.now() - user.university_email_verification_sent_at
            if time_since_last < timedelta(minutes=5):
                return False, "Please wait 5 minutes before requesting another verification email"

        return UniversityEmailVerification.send_university_verification_email(user, user.university_email)

    @staticmethod
    def request_new_university_domain(email, university_name, requester_name, notes=""):
        """Request addition of new university domain"""
        try:
            # Send email to admin for manual review
            subject = f"[InsideLab] New University Domain Request: {university_name}"
            message = f"""
New university domain verification request:

University Name: {university_name}
Email Domain: {email.split('@')[1] if '@' in email else email}
Requester: {requester_name}
Requester Email: {email}
Notes: {notes}

Please review and add this domain to the verified university domains if legitimate.
            """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@insidelab.com'],
                fail_silently=False,
            )

            logger.info(f"University domain request submitted: {university_name} - {email}")
            return True, "Domain request submitted for review"

        except Exception as e:
            logger.error(f"Failed to submit university domain request: {str(e)}")
            return False, "Failed to submit domain request"