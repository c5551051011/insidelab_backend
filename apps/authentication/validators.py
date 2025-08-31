# apps/authentication/validators.py
from django.core.exceptions import ValidationError
import re

def validate_edu_email(value):
    """Validate that email is from an educational institution"""
    if not value.lower().endswith('.edu'):
        # Check for common international education domains
        edu_domains = [
            '.edu', '.ac.uk', '.edu.cn', '.edu.au', '.edu.ca',
            '.ac.jp', '.ac.kr', '.edu.sg', '.edu.hk', '.edu.tw',
            '.ac.in', '.edu.in', '.ac.il', '.edu.br', '.edu.mx'
        ]
        
        if not any(value.lower().endswith(domain) for domain in edu_domains):
            raise ValidationError(
                'Please use an email address from an educational institution (.edu or equivalent)'
            )

