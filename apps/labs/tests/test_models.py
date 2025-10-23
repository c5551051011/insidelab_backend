from django.test import TestCase
from decimal import Decimal
from apps.labs.models import (
    Lab, ResearchTopic, Publication, RecruitmentStatus, LabCategoryAverage
)
from apps.universities.models import (
    University, Department, UniversityDepartment, Professor, ResearchGroup
)
from apps.reviews.models import Review, ReviewRating, RatingCategory
from apps.authentication.models import User


class LabModelTest(TestCase):
    """Test cases for Lab model"""

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
        self.uni_dept = UniversityDepartment.objects.create(
            university=self.university,
            department=self.department
        )
        self.professor = Professor.objects.create(
            name="Dr. Test Professor",
            email="prof@test.edu",
            university_department=self.uni_dept
        )

    def test_create_lab(self):
        """Test creating a lab"""
        lab = Lab.objects.create(
            name="AI Research Lab",
            professor=self.professor,
            description="Leading AI research laboratory",
            lab_size=15
        )
        self.assertEqual(lab.name, "AI Research Lab")
        self.assertEqual(lab.professor, self.professor)
        self.assertEqual(lab.lab_size, 15)
        self.assertEqual(lab.overall_rating, 0)
        self.assertEqual(lab.review_count, 0)

    def test_lab_auto_populate_university_department(self):
        """Test lab auto-populates university department from professor"""
        lab = Lab.objects.create(
            name="Test Lab",
            professor=self.professor
        )
        lab.save()
        self.assertEqual(lab.university_department, self.uni_dept)
        self.assertEqual(lab.university, self.university)

    def test_lab_with_research_group(self):
        """Test creating lab with research group"""
        research_group = ResearchGroup.objects.create(
            name="ML Research Group",
            university_department=self.uni_dept
        )
        self.professor.research_group = research_group
        self.professor.save()

        lab = Lab.objects.create(
            name="ML Lab",
            professor=self.professor
        )
        self.assertEqual(lab.research_group, research_group)

    def test_lab_with_research_areas_and_tags(self):
        """Test lab with research areas and tags"""
        lab = Lab.objects.create(
            name="Test Lab",
            professor=self.professor,
            research_areas=["Machine Learning", "Computer Vision"],
            tags=["AI", "Deep Learning"]
        )
        self.assertEqual(len(lab.research_areas), 2)
        self.assertEqual(len(lab.tags), 2)

    def test_lab_str_representation(self):
        """Test lab string representation"""
        lab = Lab.objects.create(
            name="Test Lab",
            professor=self.professor
        )
        expected = f"Test Lab - {self.professor.name}"
        self.assertEqual(str(lab), expected)


class ResearchTopicModelTest(TestCase):
    """Test cases for ResearchTopic model"""

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
            professor=professor
        )

    def test_create_research_topic(self):
        """Test creating a research topic"""
        topic = ResearchTopic.objects.create(
            lab=self.lab,
            title="Deep Learning for Medical Imaging",
            description="Applying deep learning to medical image analysis",
            keywords=["Deep Learning", "Medical Imaging", "CNN"],
            funding_info="NSF Grant #12345"
        )
        self.assertEqual(topic.title, "Deep Learning for Medical Imaging")
        self.assertEqual(len(topic.keywords), 3)
        self.assertEqual(topic.lab, self.lab)

    def test_research_topic_relationship(self):
        """Test research topic relationship with lab"""
        ResearchTopic.objects.create(
            lab=self.lab,
            title="Topic 1",
            description="Description 1"
        )
        ResearchTopic.objects.create(
            lab=self.lab,
            title="Topic 2",
            description="Description 2"
        )
        self.assertEqual(self.lab.research_topics.count(), 2)


class PublicationModelTest(TestCase):
    """Test cases for Publication model"""

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
            professor=professor
        )

    def test_create_publication(self):
        """Test creating a publication"""
        pub = Publication.objects.create(
            lab=self.lab,
            title="Novel Deep Learning Architecture",
            authors=["John Doe", "Jane Smith"],
            venue="NeurIPS 2024",
            year=2024,
            citations=50,
            url="https://example.com/paper"
        )
        self.assertEqual(pub.title, "Novel Deep Learning Architecture")
        self.assertEqual(len(pub.authors), 2)
        self.assertEqual(pub.year, 2024)
        self.assertEqual(pub.citations, 50)

    def test_publication_ordering(self):
        """Test publications are ordered by year and citations"""
        Publication.objects.create(
            lab=self.lab,
            title="Old Paper",
            venue="Conference",
            year=2020,
            citations=10
        )
        Publication.objects.create(
            lab=self.lab,
            title="Recent Paper",
            venue="Conference",
            year=2024,
            citations=100
        )
        pubs = self.lab.recent_publications.all()
        self.assertEqual(pubs[0].title, "Recent Paper")


class RecruitmentStatusModelTest(TestCase):
    """Test cases for RecruitmentStatus model"""

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
            professor=professor
        )

    def test_create_recruitment_status(self):
        """Test creating recruitment status"""
        status = RecruitmentStatus.objects.create(
            lab=self.lab,
            is_recruiting_phd=True,
            is_recruiting_postdoc=False,
            is_recruiting_intern=True,
            notes="Looking for students with ML background"
        )
        self.assertTrue(status.is_recruiting_phd)
        self.assertFalse(status.is_recruiting_postdoc)
        self.assertTrue(status.is_recruiting_intern)

    def test_recruitment_status_one_to_one(self):
        """Test recruitment status has one-to-one relationship with lab"""
        RecruitmentStatus.objects.create(
            lab=self.lab,
            is_recruiting_phd=True
        )
        with self.assertRaises(Exception):
            RecruitmentStatus.objects.create(
                lab=self.lab,
                is_recruiting_phd=False
            )


class LabCategoryAverageModelTest(TestCase):
    """Test cases for LabCategoryAverage model"""

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
            professor=self.professor
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
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_create_lab_category_average(self):
        """Test creating lab category average"""
        avg = LabCategoryAverage.objects.create(
            lab=self.lab,
            category=self.category,
            average_rating=Decimal('4.5'),
            review_count=10
        )
        self.assertEqual(avg.average_rating, Decimal('4.5'))
        self.assertEqual(avg.review_count, 10)

    def test_lab_category_average_unique_together(self):
        """Test lab-category combination must be unique"""
        LabCategoryAverage.objects.create(
            lab=self.lab,
            category=self.category,
            average_rating=Decimal('4.0')
        )
        with self.assertRaises(Exception):
            LabCategoryAverage.objects.create(
                lab=self.lab,
                category=self.category,
                average_rating=Decimal('3.0')
            )

    def test_update_lab_averages(self):
        """Test updating lab averages"""
        # Create a review with ratings
        review = Review.objects.create(
            lab=self.lab,
            user=self.user,
            position='PhD Student',
            duration='2 years',
            rating=Decimal('4.5'),
            review_text='Great lab!'
        )
        ReviewRating.objects.create(
            review=review,
            category=self.category,
            rating=Decimal('4.5')
        )

        # Update averages
        LabCategoryAverage.update_lab_averages(self.lab.id)

        # Check if average was created
        avg = LabCategoryAverage.objects.get(lab=self.lab, category=self.category)
        self.assertEqual(avg.average_rating, Decimal('4.5'))
        self.assertEqual(avg.review_count, 1)

    def test_lab_category_average_str(self):
        """Test string representation"""
        avg = LabCategoryAverage.objects.create(
            lab=self.lab,
            category=self.category,
            average_rating=Decimal('4.5')
        )
        expected = f"Test Lab - Work-Life Balance: 4.5"
        self.assertEqual(str(avg), expected)
