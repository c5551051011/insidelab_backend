# apps/authentication/email_backends.py
import resend
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ResendEmailBackend(BaseEmailBackend):
    """
    Custom email backend using Resend API
    Railway-compatible alternative to SMTP
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)
        if self.api_key:
            resend.api_key = self.api_key

    def send_messages(self, email_messages):
        """Send email messages using Resend API"""
        logger.info(f"🔍 DEBUG: Attempting to send {len(email_messages)} email(s)")
        logger.info(f"🔍 DEBUG: API key configured: {'Yes' if self.api_key else 'No'}")

        if not self.api_key:
            logger.error("RESEND_API_KEY not configured")
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                logger.info(f"🔍 DEBUG: Sending email to {message.to} from {message.from_email}")
                # Prepare email data for Resend
                email_data = {
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                    "text": message.body,
                }

                # Add HTML content if available
                if hasattr(message, 'alternatives') and message.alternatives:
                    for content, content_type in message.alternatives:
                        if content_type == 'text/html':
                            email_data["html"] = content
                            break

                # Send email via Resend API
                response = resend.Emails.send(email_data)

                if response.get('id'):
                    logger.info(f"Email sent successfully via Resend: {response['id']}")
                    num_sent += 1
                else:
                    logger.error(f"Failed to send email via Resend: {response}")
                    if not self.fail_silently:
                        raise Exception(f"Resend API error: {response}")

            except Exception as e:
                logger.error(f"Error sending email via Resend: {str(e)}")
                if not self.fail_silently:
                    raise

        return num_sent