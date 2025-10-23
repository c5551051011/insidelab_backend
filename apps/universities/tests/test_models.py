from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.universities.models import (
    University, Department, UniversityDepartment,
    ResearchGroup, Professor, UniversityEmailDomain
)


class UniversityModelTest(TestCase):
    """Test cases for University model"""

    def test_create_university(self):
        """Test creating a university"""
        university = University.objects.create(
            name="Stanford University",
            country="USA",
            state="California",
            city="Stanford",
            website="https://www.stanford.edu",
            ranking=3
        )
        self.assertEqual(university.name, "Stanford University")
        self.assertEqual(university.country, "USA")
        self.assertEqual(str(university), "Stanford University")

    def test_university_ordering(self):
        """Test universities are ordered by name"""
        University.objects.create(name="Z University", country="USA", state="CA", city="City")
        University.objects.create(name="A University", country="USA", state="CA", city="City")
        universities = University.objects.all()
        self.assertEqual(universities[0].name, "A University")
        self.assertEqual(universities[1].name, "Z University")


class DepartmentModelTest(TestCase):
    """Test cases for Department model"""

    def test_create_department(self):
        """Test creating a department"""
        department = Department.objects.create(
            name="Computer Science",
            description="Department of Computer Science",
            common_names=["CS", "CompSci", "Computer Sci"]
        )
        self.assertEqual(department.name, "Computer Science")
        self.assertEqual(len(department.common_names), 3)
        self.assertEqual(str(department), "Computer Science")

    def test_department_unique_name(self):
        """Test department name must be unique"""
        Department.objects.create(name="Computer Science")
        with self.assertRaises(Exception):
            Department.objects.create(name="Computer Science")


class UniversityDepartmentModelTest(TestCase):
    """Test cases for UniversityDepartment model"""

    def setUp(self):
        self.university = University.objects.create(
            name="MIT",
            country="USA",
            state="MA",
            city="Cambridge"
        )
        self.department = Department.objects.create(
            name="Electrical Engineering"
        )

    def test_create_university_department(self):
        """Test creating a university-department relationship"""
        uni_dept = UniversityDepartment.objects.create(
            university=self.university,
            department=self.department,
            local_name="EECS",
            website="https://www.eecs.mit.edu"
        )
        self.assertEqual(uni_dept.university, self.university)
        self.assertEqual(uni_dept.department, self.department)
        self.assertEqual(uni_dept.local_name, "EECS")

    def test_university_department_display_name(self):
        """Test display name property"""
        uni_dept = UniversityDepartment.objects.create(
            university=self.university,
            department=self.department,
            local_name="EECS"
        )
        self.assertEqual(uni_dept.display_name, "EECS")

        uni_dept_no_local = UniversityDepartment.objects.create(
            university=University.objects.create(name="Test U", country="USA", state="CA", city="Test"),
            department=self.department
        )
        self.assertEqual(uni_dept_no_local.display_name, "Electrical Engineering")

    def test_university_department_unique_together(self):
        """Test university-department combination must be unique"""
        UniversityDepartment.objects.create(
            university=self.university,
            department=self.department
        )
        with self.assertRaises(Exception):
            UniversityDepartment.objects.create(
                university=self.university,
                department=self.department
            )


class ResearchGroupModelTest(TestCase):
    """Test cases for ResearchGroup model"""

    def setUp(self):
        self.university = University.objects.create(
            name="Berkeley",
            country="USA",
            state="CA",
            city="Berkeley"
        )
        self.department = Department.objects.create(
            name="Computer Science"
        )
        self.uni_dept = UniversityDepartment.objects.create(
            university=self.university,
            department=self.department
        )

    def test_create_research_group(self):
        """Test creating a research group"""
        group = ResearchGroup.objects.create(
            name="AI Research Lab",
            university_department=self.uni_dept,
            description="Artificial Intelligence Research",
            research_areas=["Machine Learning", "Deep Learning"]
        )
        self.assertEqual(group.name, "AI Research Lab")
        self.assertEqual(len(group.research_areas), 2)
        self.assertEqual(group.university, self.university)
        self.assertEqual(group.department, self.department)

    def test_research_group_unique_per_department(self):
        """Test research group name must be unique per university department"""
        ResearchGroup.objects.create(
            name="AI Lab",
            university_department=self.uni_dept
        )
        with self.assertRaises(Exception):
            ResearchGroup.objects.create(
                name="AI Lab",
                university_department=self.uni_dept
            )


class ProfessorModelTest(TestCase):
    """Test cases for Professor model"""

    def setUp(self):
        self.university = University.objects.create(
            name="Harvard",
            country="USA",
            state="MA",
            city="Cambridge"
        )
        self.department = Department.objects.create(
            name="Computer Science"
        )
        self.uni_dept = UniversityDepartment.objects.create(
            university=self.university,
            department=self.department
        )

    def test_create_professor(self):
        """Test creating a professor"""
        professor = Professor.objects.create(
            name="Dr. John Smith",
            email="jsmith@harvard.edu",
            university_department=self.uni_dept,
            research_interests=["AI", "Machine Learning"],
            bio="Leading researcher in AI"
        )
        self.assertEqual(professor.name, "Dr. John Smith")
        self.assertEqual(professor.email, "jsmith@harvard.edu")
        self.assertEqual(len(professor.research_interests), 2)

    def test_professor_with_research_group(self):
        """Test creating a professor with research group"""
        group = ResearchGroup.objects.create(
            name="AI Lab",
            university_department=self.uni_dept
        )
        professor = Professor.objects.create(
            name="Dr. Jane Doe",
            email="jdoe@harvard.edu",
            university_department=self.uni_dept,
            research_group=group
        )
        self.assertEqual(professor.research_group, group)


class UniversityEmailDomainModelTest(TestCase):
    """Test cases for UniversityEmailDomain model"""

    def setUp(self):
        self.university = University.objects.create(
            name="KAIST",
            country="South Korea",
            state="Daejeon",
            city="Daejeon"
        )

    def test_create_email_domain(self):
        """Test creating a university email domain"""
        domain = UniversityEmailDomain.objects.create(
            university=self.university,
            domain="kaist.ac.kr",
            is_active=True,
            is_verified=True,
            verification_type='official'
        )
        self.assertEqual(domain.domain, "kaist.ac.kr")
        self.assertTrue(domain.is_active)
        self.assertTrue(domain.is_verified)

    def test_email_domain_unique(self):
        """Test email domain must be unique"""
        UniversityEmailDomain.objects.create(
            university=self.university,
            domain="kaist.ac.kr",
            is_verified=True
        )
        with self.assertRaises(Exception):
            UniversityEmailDomain.objects.create(
                university=self.university,
                domain="kaist.ac.kr",
                is_verified=True
            )

    def test_is_university_email_classmethod(self):
        """Test checking if email is a university email"""
        UniversityEmailDomain.objects.create(
            university=self.university,
            domain="kaist.ac.kr",
            is_active=True,
            is_verified=True
        )

        self.assertTrue(UniversityEmailDomain.is_university_email("student@kaist.ac.kr"))
        self.assertFalse(UniversityEmailDomain.is_university_email("user@gmail.com"))
        self.assertFalse(UniversityEmailDomain.is_university_email("invalid-email"))

    def test_get_university_by_email_classmethod(self):
        """Test getting university by email domain"""
        UniversityEmailDomain.objects.create(
            university=self.university,
            domain="kaist.ac.kr",
            is_active=True,
            is_verified=True
        )

        university = UniversityEmailDomain.get_university_by_email("student@kaist.ac.kr")
        self.assertEqual(university, self.university)

        university_none = UniversityEmailDomain.get_university_by_email("user@gmail.com")
        self.assertIsNone(university_none)

    def test_inactive_domain_not_recognized(self):
        """Test that inactive domains are not recognized"""
        UniversityEmailDomain.objects.create(
            university=self.university,
            domain="old.kaist.ac.kr",
            is_active=False,
            is_verified=True
        )

        self.assertFalse(UniversityEmailDomain.is_university_email("student@old.kaist.ac.kr"))
