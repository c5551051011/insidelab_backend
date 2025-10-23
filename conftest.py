"""
Pytest configuration file for Django project
"""
import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Configure test database
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests
    """
    pass


@pytest.fixture
def api_client():
    """
    Create an API client for testing
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """
    Create an authenticated API client
    """
    from apps.authentication.models import User
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def sample_university():
    """
    Create a sample university for testing
    """
    from apps.universities.models import University
    return University.objects.create(
        name="Test University",
        country="USA",
        state="CA",
        city="Test City"
    )


@pytest.fixture
def sample_department():
    """
    Create a sample department for testing
    """
    from apps.universities.models import Department
    return Department.objects.create(
        name="Computer Science"
    )


@pytest.fixture
def sample_university_department(sample_university, sample_department):
    """
    Create a sample university department for testing
    """
    from apps.universities.models import UniversityDepartment
    return UniversityDepartment.objects.create(
        university=sample_university,
        department=sample_department
    )


@pytest.fixture
def sample_professor(sample_university_department):
    """
    Create a sample professor for testing
    """
    from apps.universities.models import Professor
    return Professor.objects.create(
        name="Dr. Test Professor",
        email="prof@test.edu",
        university_department=sample_university_department
    )


@pytest.fixture
def sample_lab(sample_professor):
    """
    Create a sample lab for testing
    """
    from apps.labs.models import Lab
    return Lab.objects.create(
        name="Test Lab",
        professor=sample_professor,
        description="A test laboratory"
    )


@pytest.fixture
def sample_rating_category():
    """
    Create a sample rating category for testing
    """
    from apps.reviews.models import RatingCategory
    return RatingCategory.objects.create(
        name="work_life_balance",
        display_name="Work-Life Balance",
        is_active=True,
        sort_order=1
    )
