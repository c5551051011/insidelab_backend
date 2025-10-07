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

        # Get domain - always use Railway for email links
        if request:
            try:
                host = request.get_host()
                # Always use Railway domain for email verification links
                if 'localhost' in host or '127.0.0.1' in host:
                    # For local development, still use Railway domain in emails
                    domain = 'insidelab.up.railway.app'
                    protocol = 'https'
                else:
                    # Production environment
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

        # Determine language and templates
        language = getattr(user, 'language', 'ko')  # Default to Korean for backward compatibility

        # Auto-detect language from email domain if not set
        if language == 'ko' and user.email:
            # Check if email domain suggests English (common international domains)
            email_domain = user.email.split('@')[1].lower()
            international_domains = [
                'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com',
                'edu', '.edu', 'university', 'college', 'ac.uk', 'ox.ac.uk',
                'cam.ac.uk', 'mit.edu', 'stanford.edu', 'harvard.edu'
            ]

            if any(domain in email_domain for domain in international_domains):
                # Check for Korean domains to stay Korean
                korean_domains = [
                    '.ac.kr', '.edu.kr', 'kaist.ac.kr', 'snu.ac.kr',
                    'yonsei.ac.kr', 'korea.ac.kr', 'postech.ac.kr'
                ]
                if not any(kr_domain in email_domain for kr_domain in korean_domains):
                    language = 'en'

        # Select templates based on language
        html_template = f'emails/verification_{language}.html'
        text_template = f'emails/verification_{language}.txt'

        # Fallback to Korean if English templates don't exist
        try:
            html_content = render_to_string(html_template, context)
            text_content = render_to_string(text_template, context)
        except Exception:
            # Fallback to Korean templates
            html_content = render_to_string('emails/verification_ko.html', context)
            text_content = render_to_string('emails/verification_ko.txt', context)
            language = 'ko'

        # Email subject based on language
        if language == 'en':
            subject = '🔬 InsideLab - Please Verify Your Email Address'
        else:
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

        logger.info(f"Verification email sent successfully to {user.email} in {language}")
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


def send_feedback_email(user_email, user_name, subject, message, user_type="user"):
    """
    Send feedback email to InsideLab team

    Args:
        user_email: User's email address
        user_name: User's name
        subject: Email subject from client
        message: Feedback message from client
        user_type: Type of user (user, anonymous, etc.)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email context for feedback
        context = {
            'user_email': user_email,
            'user_name': user_name or user_email.split('@')[0],
            'user_type': user_type,
            'feedback_subject': subject,
            'feedback_message': message,
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        }

        # Render templates
        html_content = render_to_string('emails/feedback.html', context)
        text_content = render_to_string('emails/feedback.txt', context)

        # Email subject for internal team
        email_subject = f'🔬 InsideLab Feedback: {subject}'

        # Create email to InsideLab team
        email = EmailMultiAlternatives(
            subject=email_subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'InsideLab <noreply@insidelab.com>'),
            to=['insidelab25@gmail.com'],
            reply_to=[user_email]  # Allow team to reply directly to user
        )

        # Attach HTML version
        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send()

        logger.info(f"Feedback email sent successfully from {user_email} with subject: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send feedback email from {user_email}: {str(e)}")
        return False