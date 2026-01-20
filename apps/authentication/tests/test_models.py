from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.authentication.models import User, UserLabInterest
from apps.universities.models import University, Department, UniversityDepartment
from apps.labs.models import Lab
from apps.universities.models import Professor


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        """Set up test data"""
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

    def test_create_user_with_email(self):
        """Test creating a user with email"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_verified)

    def test_user_email_unique(self):
        """Test that email must be unique"""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='pass123'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='pass123'
            )

    def test_user_with_university_department(self):
        """Test user creation with university department"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            university_department=self.university_department
        )
        user.save()

        self.assertEqual(user.university_department, self.university_department)
        self.assertEqual(user.university, self.university)
        self.assertEqual(user.university_department.department.name, "Computer Science")

    def test_user_display_name(self):
        """Test user display name property"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.assertEqual(user.display_name, 'Test User')

        user_no_name = User.objects.create_user(
            username='testuser2',
            email='noname@example.com',
            password='testpass123'
        )
        self.assertEqual(user_no_name.display_name, 'noname')

    def test_user_verification_badge(self):
        """Test user verification badge property"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.verification_badge, "Unverified")

        user.is_verified = True
        user.university_department = self.university_department
        user.save()
        self.assertIn("Computer Science", user.verification_badge)
        self.assertIn("Test University", user.verification_badge)


class UserLabInterestModelTest(TestCase):
    """Test cases for UserLabInterest model"""

    def setUp(self):
        """Set up test data"""
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
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_user_lab_interest(self):
        """Test creating a user lab interest"""
        interest = UserLabInterest.objects.create(
            user=self.user,
            lab=self.lab,
            interest_type='general'
        )
        self.assertEqual(interest.user, self.user)
        self.assertEqual(interest.lab, self.lab)
        self.assertEqual(interest.interest_type, 'general')

    def test_user_lab_interest_unique_together(self):
        """Test that user-lab combination must be unique"""
        UserLabInterest.objects.create(
            user=self.user,
            lab=self.lab,
            interest_type='general'
        )
        with self.assertRaises(Exception):
            UserLabInterest.objects.create(
                user=self.user,
                lab=self.lab,
                interest_type='application'
            )

    def test_user_lab_interest_with_notes(self):
        """Test creating interest with notes"""
        interest = UserLabInterest.objects.create(
            user=self.user,
            lab=self.lab,
            interest_type='application',
            notes='Interested in machine learning research'
        )
        self.assertEqual(interest.notes, 'Interested in machine learning research')
