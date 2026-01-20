from django.test import TestCase
from decimal import Decimal
from apps.reviews.models import RatingCategory, Review, ReviewRating, ReviewHelpful
from apps.labs.models import Lab
from apps.universities.models import University, Department, UniversityDepartment, Professor
from apps.authentication.models import User


class RatingCategoryModelTest(TestCase):
    """Test cases for RatingCategory model"""

    def test_create_rating_category(self):
        """Test creating a rating category"""
        # Use get_or_create since migration already creates this category
        category, created = RatingCategory.objects.get_or_create(
            name="work_life_balance",
            defaults={
                'display_name': "Work-Life Balance",
                'description': "Balance between work and personal life",
                'is_active': True,
                'sort_order': 3
            }
        )
        self.assertEqual(category.name, "work_life_balance")
        self.assertEqual(category.display_name, "Work-Life Balance")
        self.assertTrue(category.is_active)
        self.assertEqual(str(category), "Work-Life Balance")

    def test_rating_category_ordering(self):
        """Test categories are ordered by sort_order"""
        # Use unique names to avoid conflicts with migration data
        RatingCategory.objects.get_or_create(
            name="test_category_2",
            defaults={
                'display_name': "Second Category",
                'sort_order': 100
            }
        )
        RatingCategory.objects.get_or_create(
            name="test_category_1",
            defaults={
                'display_name': "First Category",
                'sort_order': 99
            }
        )
        # Get only test categories
        categories = RatingCategory.objects.filter(name__startswith='test_').order_by('sort_order')
        self.assertEqual(categories[0].display_name, "First Category")
        self.assertEqual(categories[1].display_name, "Second Category")

    def test_rating_category_unique_name(self):
        """Test category name must be unique"""
        RatingCategory.objects.create(
            name="unique_category",
            display_name="Unique"
        )
        with self.assertRaises(Exception):
            RatingCategory.objects.create(
                name="unique_category",
                display_name="Another Unique"
            )


class ReviewModelTest(TestCase):
    """Test cases for Review model"""

    def setUp(self):
        """Set up test data"""
        self.university = University.objects.create(
            name="Test University",
            country="USA",
            state="CA",
            city="Test City"
        )
        self.department = Department.objects.create(name="CS")
        self.uni_dept = UniversityDepartment.objects.create(
            university=self.university,
            department=self.department
        )
        self.professor = Professor.objects.create(
            name="Dr. Test",
            university_department=self.uni_dept
        )
        self.lab = Lab.objects.create(
            name="Test Lab",
            head_professor=self.professor
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_create_review(self):
        """Test creating a review"""
        review = Review.objects.create(
            lab=self.lab,
            user=self.user,
            position='PhD Student',
            duration='2 years',
            rating=Decimal('4.5'),
            review_text='Great research environment!',
            pros=["Good mentorship", "Interesting projects"],
            cons=["Long hours"]
        )
        self.assertEqual(review.lab, self.lab)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, Decimal('4.5'))
        self.assertEqual(len(review.pros), 2)
        self.assertEqual(len(review.cons), 1)

    def test_review_unique_together(self):
        """Test user can only review a lab once"""
        Review.objects.create(
            lab=self.lab,
            user=self.user,
            position='PhD Student',
            duration='1 year',
            rating=Decimal('4.0'),
            review_text='Good lab'
        )
        with self.assertRaises(Exception):
            Review.objects.create(
                lab=self.lab,
                user=self.user,
                position='PhD Student',
                duration='2 years',
                rating=Decimal('5.0'),
                review_text='Another review'
            )

    def test_review_default_status(self):
        """Test review has default status of active"""
        review = Review.objects.create(
            lab=self.lab,
            user=self.user,
            position='PhD Student',
            duration='1 year',
            rating=Decimal('4.0'),
            review_text='Test review'
        )
        self.assertEqual(review.status, 'active')
        self.assertFalse(review.is_verified)
        self.assertEqual(review.helpful_count, 0)

    def test_review_str_representation(self):
        """Test review string representation"""
        review = Review.objects.create(
            lab=self.lab,
            user=self.user,
            position='PhD Student',
            duration='1 year',
            rating=Decimal('4.0'),
            review_text='Test'
        )
        expected = f"Review for {self.lab.name} by {self.user.email}"
        self.assertEqual(str(review), expected)


class ReviewRatingModelTest(TestCase):
    """Test cases for ReviewRating model"""

    def setUp(self):
        """Set up test data"""
        university = University.objects.create(
            name="Test University",
            country="USA",
            state="CA",
            city="Test City"
        )
        department = Department.objects.create(name="CS")
        uni_dept = UniversityDepartment.objects.create(
            university=university,
            department=department
        )
        professor = Professor.objects.create(
            name="Dr. Test",
            university_department=uni_dept
        )
        self.lab = Lab.objects.create(
            name="Test Lab",
            head_professor=professor
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.review = Review.objects.create(
            lab=self.lab,
            user=self.user,
            position='PhD Student',
            duration='1 year',
            rating=Decimal('4.0'),
            review_text='Test review'
        )
        # Use get_or_create to get existing category from migration
        self.category, _ = RatingCategory.objects.get_or_create(
            name="work_life_balance",
            defaults={
                'display_name': "Work-Life Balance",
                'is_active': True,
                'sort_order': 3
            }
        )

    def test_create_review_rating(self):
        """Test creating a review rating"""
        rating = ReviewRating.objects.create(
            review=self.review,
            category=self.category,
            rating=Decimal('4.5')
        )
        self.assertEqual(rating.review, self.review)
        self.assertEqual(rating.category, self.category)
        self.assertEqual(rating.rating, Decimal('4.5'))

    def test_review_rating_unique_together(self):
        """Test review-category combination must be unique"""
        ReviewRating.objects.create(
            review=self.review,
            category=self.category,
            rating=Decimal('4.0')
        )
        with self.assertRaises(Exception):
            ReviewRating.objects.create(
                review=self.review,
                category=self.category,
                rating=Decimal('5.0')
            )

    def test_review_rating_validation(self):
        """Test rating value validation (0-5)"""
        # Valid rating
        rating = ReviewRating.objects.create(
            review=self.review,
            category=self.category,
            rating=Decimal('5.0')
        )
        self.assertEqual(rating.rating, Decimal('5.0'))

    def test_category_ratings_dict(self):
        """Test getting category ratings as dictionary"""
        ReviewRating.objects.create(
            review=self.review,
            category=self.category,
            rating=Decimal('4.5')
        )
        ratings_dict = self.review.category_ratings_dict
        self.assertIn("Work-Life Balance", ratings_dict)
        self.assertEqual(ratings_dict["Work-Life Balance"], 4.5)

    def test_set_category_ratings(self):
        """Test setting category ratings from dictionary"""
        # Use get_or_create for second category (mentorship_quality exists in migration)
        category2, _ = RatingCategory.objects.get_or_create(
            name="mentorship_quality",
            defaults={
                'display_name': "Mentorship Quality",
                'is_active': True,
                'sort_order': 1
            }
        )
        ratings_dict = {
            "Work-Life Balance": 4.5,
            "Mentorship Quality": 4.8  # matches migration display_name
        }
        self.review.set_category_ratings(ratings_dict)

        self.assertEqual(self.review.category_ratings.count(), 2)
        rating1 = ReviewRating.objects.get(review=self.review, category=self.category)
        self.assertEqual(rating1.rating, Decimal('4.5'))


class ReviewHelpfulModelTest(TestCase):
    """Test cases for ReviewHelpful model"""

    def setUp(self):
        """Set up test data"""
        university = University.objects.create(
            name="Test University",
            country="USA",
            state="CA",
            city="Test City"
        )
        department = Department.objects.create(name="CS")
        uni_dept = UniversityDepartment.objects.create(
            university=university,
            department=department
        )
        professor = Professor.objects.create(
            name="Dr. Test",
            university_department=uni_dept
        )
        self.lab = Lab.objects.create(
            name="Test Lab",
            head_professor=professor
        )
        self.reviewer = User.objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="testpass123"
        )
        self.voter = User.objects.create_user(
            username="voter",
            email="voter@example.com",
            password="testpass123"
        )
        self.review = Review.objects.create(
            lab=self.lab,
            user=self.reviewer,
            position='PhD Student',
            duration='1 year',
            rating=Decimal('4.0'),
            review_text='Test review'
        )

    def test_create_helpful_vote(self):
        """Test creating a helpful vote"""
        vote = ReviewHelpful.objects.create(
            review=self.review,
            user=self.voter,
            is_helpful=True
        )
        self.assertEqual(vote.review, self.review)
        self.assertEqual(vote.user, self.voter)
        self.assertTrue(vote.is_helpful)

    def test_helpful_vote_unique_together(self):
        """Test user can only vote once per review"""
        ReviewHelpful.objects.create(
            review=self.review,
            user=self.voter,
            is_helpful=True
        )
        with self.assertRaises(Exception):
            ReviewHelpful.objects.create(
                review=self.review,
                user=self.voter,
                is_helpful=False
            )

    def test_unhelpful_vote(self):
        """Test creating an unhelpful vote"""
        vote = ReviewHelpful.objects.create(
            review=self.review,
            user=self.voter,
            is_helpful=False
        )
        self.assertFalse(vote.is_helpful)


class ReviewIntegrationTest(TestCase):
    """Integration tests for review system"""

    def setUp(self):
        """Set up test data"""
        university = University.objects.create(
            name="Test University",
            country="USA",
            state="CA",
            city="Test City"
        )
        department = Department.objects.create(name="CS")
        uni_dept = UniversityDepartment.objects.create(
            university=university,
            department=department
        )
        professor = Professor.objects.create(
            name="Dr. Test",
            university_department=uni_dept
        )
        self.lab = Lab.objects.create(
            name="Test Lab",
            head_professor=professor
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        # Use get_or_create to get existing categories from migration
        self.category1, _ = RatingCategory.objects.get_or_create(
            name="work_life_balance",
            defaults={
                'display_name': "Work-Life Balance",
                'is_active': True,
                'sort_order': 3
            }
        )
        self.category2, _ = RatingCategory.objects.get_or_create(
            name="mentorship_quality",
            defaults={
                'display_name': "Mentorship Quality",
                'is_active': True,
                'sort_order': 1
            }
        )

    def test_review_with_multiple_category_ratings(self):
        """Test creating review with multiple category ratings"""
        review = Review.objects.create(
            lab=self.lab,
            user=self.user,
            position='PhD Student',
            duration='2 years',
            rating=Decimal('4.5'),
            review_text='Excellent lab!'
        )

        ReviewRating.objects.create(
            review=review,
            category=self.category1,
            rating=Decimal('4.5')
        )
        ReviewRating.objects.create(
            review=review,
            category=self.category2,
            rating=Decimal('4.8')
        )

        self.assertEqual(review.category_ratings.count(), 2)
        ratings_dict = review.category_ratings_dict
        self.assertEqual(len(ratings_dict), 2)
