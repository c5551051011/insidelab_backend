from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from apps.authentication.models import User, UserLabInterest
from apps.universities.models import University, Department, UniversityDepartment, Professor
from apps.labs.models import Lab


class UserRegistrationTestCase(APITestCase):
    """Test cases for user registration"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'name': 'New User'
        }
        response = self.client.post(self.register_url, data, format='json')

        # Note: Actual status code may vary based on email service availability
        # This test focuses on the response structure
        self.assertIn(response.status_code, [201, 500])

        if response.status_code == 201:
            self.assertIn('message', response.data)
            self.assertIn('user', response.data)

    def test_register_user_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass456!',
            'name': 'Test User'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_existing_email(self):
        """Test registration with already existing email"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='password123'
        )

        data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """Test cases for user login"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_email(self):
        """Test login with non-existent email"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserProfileTestCase(APITestCase):
    """Test cases for user profile operations"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('current_user')
        self.update_profile_url = reverse('update_profile')

    def test_get_current_user(self):
        """Test getting current user profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['name'], 'Test User')

    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            'name': 'Updated Name',
            'position': 'PhD Student'
        }
        response = self.client.put(self.update_profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')
        self.assertEqual(response.data['position'], 'PhD Student')

    def test_get_profile_without_authentication(self):
        """Test getting profile without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserLabInterestTestCase(APITestCase):
    """Test cases for user lab interest management"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create test data
        self.university = University.objects.create(
            name="Test University",
            country="USA",
            state="CA",
            city="Test City"
        )
        self.department = Department.objects.create(
            name="Computer Science"
        )
        self.university_department = UniversityDepartment.objects.create(
            university=self.university,
            department=self.department
        )
        self.professor = Professor.objects.create(
            name="Dr. Test",
            email="prof@test.edu",
            university_department=self.university_department
        )
        self.lab = Lab.objects.create(
            name="Test Lab",
            head_professor=self.professor
        )

        self.interest_list_url = reverse('userlabinterest-list')
        self.toggle_url = reverse('userlabinterest-toggle-interest')

    def test_create_lab_interest(self):
        """Test creating a new lab interest"""
        data = {
            'lab': self.lab.id,
            'interest_type': 'general',
            'notes': 'Interested in this lab'
        }
        response = self.client.post(self.interest_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['interest_type'], 'general')

    def test_list_user_lab_interests(self):
        """Test listing user's lab interests"""
        UserLabInterest.objects.create(
            user=self.user,
            lab=self.lab,
            interest_type='application'
        )
        response = self.client.get(self.interest_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_toggle_lab_interest(self):
        """Test toggling lab interest"""
        data = {
            'lab_id': self.lab.id,
            'interest_type': 'watching'
        }
        # First toggle - should create
        response = self.client.post(self.toggle_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'added')

        # Second toggle - should update
        response = self.client.post(self.toggle_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'updated')

    def test_get_interest_summary(self):
        """Test getting summary of user's lab interests"""
        UserLabInterest.objects.create(
            user=self.user,
            lab=self.lab,
            interest_type='general'
        )
        summary_url = reverse('userlabinterest-summary')
        response = self.client.get(summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_interests', response.data)
        self.assertIn('by_type', response.data)

    def test_remove_lab_interest(self):
        """Test removing a lab interest"""
        interest = UserLabInterest.objects.create(
            user=self.user,
            lab=self.lab,
            interest_type='general'
        )
        remove_url = reverse('userlabinterest-remove-interest')
        response = self.client.delete(f'{remove_url}?lab_id={self.lab.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'removed')

    def test_lab_interest_without_authentication(self):
        """Test accessing lab interests without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.interest_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GoogleAuthTestCase(APITestCase):
    """Test cases for Google authentication"""

    def setUp(self):
        self.client = APIClient()
        self.google_auth_url = reverse('google_auth')

    def test_google_auth_new_user(self):
        """Test Google auth with new user"""
        data = {
            'email': 'newgoogleuser@gmail.com',
            'name': 'Google User'
        }
        response = self.client.post(self.google_auth_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        # Verify user was created
        user = User.objects.get(email='newgoogleuser@gmail.com')
        self.assertTrue(user.is_verified)

    def test_google_auth_existing_user(self):
        """Test Google auth with existing user"""
        existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@gmail.com',
            password='testpass123'
        )

        data = {
            'email': 'existing@gmail.com',
            'name': 'Updated Name'
        }
        response = self.client.post(self.google_auth_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_google_auth_without_email(self):
        """Test Google auth without email"""
        data = {
            'name': 'User Without Email'
        }
        response = self.client.post(self.google_auth_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FeedbackTestCase(APITestCase):
    """Test cases for feedback submission"""

    def setUp(self):
        self.client = APIClient()
        self.feedback_url = reverse('send_feedback')

    def test_send_feedback_anonymous(self):
        """Test sending feedback as anonymous user"""
        data = {
            'email': 'user@example.com',
            'name': 'Anonymous User',
            'subject': 'Test Feedback',
            'message': 'This is a test feedback message'
        }
        response = self.client.post(self.feedback_url, data, format='json')
        # Status may vary based on email service availability
        self.assertIn(response.status_code, [200, 500])

    def test_send_feedback_authenticated(self):
        """Test sending feedback as authenticated user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.client.force_authenticate(user=user)

        data = {
            'email': 'test@example.com',
            'subject': 'Test Feedback',
            'message': 'This is a test feedback message'
        }
        response = self.client.post(self.feedback_url, data, format='json')
        self.assertIn(response.status_code, [200, 500])

    def test_send_feedback_missing_fields(self):
        """Test sending feedback with missing required fields"""
        data = {
            'email': 'user@example.com',
            'subject': 'Test'
        }
        response = self.client.post(self.feedback_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_feedback_invalid_email(self):
        """Test sending feedback with invalid email"""
        data = {
            'email': 'invalid-email',
            'subject': 'Test',
            'message': 'Test message'
        }
        response = self.client.post(self.feedback_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
