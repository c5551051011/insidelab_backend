# apps/authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_edu_email


"""
class User(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_edu_email])
    university = models.ForeignKey(
        'universities.University', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    position = models.CharField(
        max_length=50,
        choices=[
            ('undergrad', 'Undergraduate'),
            ('ms', 'MS Student'),
            ('phd', 'PhD Student'),
            ('postdoc', 'Postdoc'),
            ('research_staff', 'Research Staff'),
            ('faculty', 'Faculty'),
        ],
        blank=True
    )
    department = models.CharField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

"""


