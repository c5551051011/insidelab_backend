"""
Management command to create example reviews for all labs.
Generates realistic reviews with diverse perspectives and ratings.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.labs.models import Lab
from apps.universities.models import University
from apps.reviews.models import Review, RatingCategory
import random
import time

User = get_user_model()


class Command(BaseCommand):
    help = 'Create example reviews for all labs with realistic data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-reviews',
            action='store_true',
            help='Clear existing reviews before creating new ones'
        )
        parser.add_argument(
            '--reviews-per-lab',
            type=int,
            default=3,
            help='Number of reviews to create per lab (default: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )

    def handle(self, *args, **options):
        start_time = time.time()

        if options['clear_reviews']:
            self.clear_reviews(options['dry_run'])

        self.create_example_users(options['dry_run'])
        self.create_reviews_for_all_labs(options['reviews_per_lab'], options['dry_run'])

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Completed in {elapsed_time:.2f} seconds')
        )

    def clear_reviews(self, dry_run):
        """Clear existing reviews"""
        if dry_run:
            self.stdout.write('DRY RUN: Would clear existing reviews')
            return

        Review.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing reviews'))

    def create_example_users(self, dry_run):
        """Create example users for reviews"""
        if dry_run:
            self.stdout.write('DRY RUN: Would create example users')
            return

        example_users = [
            {
                'email': 'alex.chen@example.com',
                'username': 'alex_chen',
                'name': 'Alex Chen',
                'position': 'PhD Student',
                'university': 'Stanford University'
            },
            {
                'email': 'maria.rodriguez@example.com',
                'username': 'maria_rodriguez',
                'name': 'Maria Rodriguez',
                'position': 'MS Student',
                'university': 'Massachusetts Institute of Technology'
            },
            {
                'email': 'david.kim@example.com',
                'username': 'david_kim',
                'name': 'David Kim',
                'position': 'PhD Student',
                'university': 'Carnegie Mellon University'
            },
            {
                'email': 'sarah.johnson@example.com',
                'username': 'sarah_johnson',
                'name': 'Sarah Johnson',
                'position': 'PostDoc',
                'university': 'University of California, Berkeley'
            },
            {
                'email': 'raj.patel@example.com',
                'username': 'raj_patel',
                'name': 'Raj Patel',
                'position': 'PhD Student',
                'university': 'Harvard University'
            },
            {
                'email': 'emily.wong@example.com',
                'username': 'emily_wong',
                'name': 'Emily Wong',
                'position': 'MS Student',
                'university': 'Princeton University'
            },
            {
                'email': 'michael.brown@example.com',
                'username': 'michael_brown',
                'name': 'Michael Brown',
                'position': 'PhD Student',
                'university': 'Cornell University'
            },
            {
                'email': 'lisa.zhang@example.com',
                'username': 'lisa_zhang',
                'name': 'Lisa Zhang',
                'position': 'Research Assistant',
                'university': 'Stanford University'
            },
            {
                'email': 'james.wilson@example.com',
                'username': 'james_wilson',
                'name': 'James Wilson',
                'position': 'PhD Student',
                'university': 'Massachusetts Institute of Technology'
            },
            {
                'email': 'anna.lee@example.com',
                'username': 'anna_lee',
                'name': 'Anna Lee',
                'position': 'MS Student',
                'university': 'University of California, Berkeley'
            }
        ]

        for user_data in example_users:
            try:
                university = University.objects.get(name=user_data['university'])
                user, created = User.objects.get_or_create(
                    email=user_data['email'],
                    defaults={
                        'username': user_data['username'],
                        'name': user_data['name'],
                        'position': user_data['position'],
                        'university': university,
                        'email_verified': True,
                        'is_verified': True,
                        'verification_status': 'verified'
                    }
                )
                if created:
                    user.set_password('example_password')
                    user.save()
                    self.stdout.write(f'Created user: {user.email}')
            except University.DoesNotExist:
                self.stdout.write(f'University not found: {user_data["university"]}')

    def create_reviews_for_all_labs(self, reviews_per_lab, dry_run):
        """Create reviews for all labs"""
        labs = Lab.objects.all()
        users = list(User.objects.filter(email__contains='@example.com'))
        categories = list(RatingCategory.objects.filter(is_active=True))

        if not users:
            self.stdout.write(self.style.ERROR('No example users found. Run without --dry-run first.'))
            return

        if dry_run:
            self.stdout.write(f'DRY RUN: Would create {reviews_per_lab} reviews for {labs.count()} labs')
            return

        total_reviews = 0

        for lab in labs:
            self.stdout.write(f'Creating reviews for: {lab.name}')

            # Select random users for this lab (avoiding duplicates)
            lab_users = random.sample(users, min(reviews_per_lab, len(users)))

            for i, user in enumerate(lab_users):
                try:
                    review_data = self.generate_review_data(lab, user, i)

                    review = Review.objects.create(
                        lab=lab,
                        user=user,
                        position=review_data['position'],
                        duration=review_data['duration'],
                        rating=review_data['overall_rating'],
                        review_text=review_data['review_text'],
                        pros=review_data['pros'],
                        cons=review_data['cons'],
                        is_verified=random.choice([True, False]),
                        helpful_count=random.randint(0, 15)
                    )

                    # Set category ratings
                    review.set_category_ratings(review_data['category_ratings'])

                    total_reviews += 1
                    self.stdout.write(f'  + Created review by {user.name}')

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to create review: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {total_reviews} reviews across {labs.count()} labs')
        )

    def generate_review_data(self, lab, user, review_index):
        """Generate realistic review data for a lab"""

        # Vary review quality - some labs get better reviews
        lab_quality_bias = self.get_lab_quality_bias(lab.name)

        # Generate category ratings
        category_ratings = {}
        categories = RatingCategory.objects.filter(is_active=True)

        for category in categories:
            # Add some variation around the lab quality bias
            base_rating = lab_quality_bias + random.uniform(-0.5, 0.5)
            rating = max(1.0, min(5.0, base_rating))
            category_ratings[category.display_name] = round(rating, 1)

        # Calculate overall rating (average of categories with some noise)
        overall_rating = sum(category_ratings.values()) / len(category_ratings)
        overall_rating += random.uniform(-0.3, 0.3)
        overall_rating = max(1.0, min(5.0, overall_rating))

        # Generate review content based on rating
        review_content = self.generate_review_content(lab, overall_rating, review_index)

        return {
            'position': random.choice(['PhD Student', 'MS Student', 'PostDoc', 'Research Assistant']),
            'duration': random.choice(['1 year', '2 years', '3 years', '4+ years', '6 months']),
            'overall_rating': round(overall_rating, 1),
            'category_ratings': category_ratings,
            'review_text': review_content['text'],
            'pros': review_content['pros'],
            'cons': review_content['cons']
        }

    def get_lab_quality_bias(self, lab_name):
        """Get quality bias for different labs (some are more prestigious)"""
        # Top-tier labs get higher bias
        top_tier_keywords = ['SAIL', 'BAIR', 'CSAIL', 'MIT', 'Stanford', 'Robotics Institute']
        mid_tier_keywords = ['Graphics', 'Vision', 'NLP', 'Security', 'Theory']

        lab_lower = lab_name.lower()

        if any(keyword.lower() in lab_lower for keyword in top_tier_keywords):
            return random.uniform(4.0, 4.8)  # Very high ratings
        elif any(keyword.lower() in lab_lower for keyword in mid_tier_keywords):
            return random.uniform(3.5, 4.3)  # Good ratings
        else:
            return random.uniform(3.0, 4.5)  # Mixed ratings

    def generate_review_content(self, lab, rating, review_index):
        """Generate realistic review content"""

        # Content templates based on research area
        research_area = lab.research_areas[0] if lab.research_areas else "Computer Science"

        # Positive review templates
        positive_templates = [
            f"Excellent research environment in {research_area}. The lab provides outstanding mentorship and cutting-edge projects.",
            f"Amazing experience working on {research_area} projects. Great work-life balance and supportive team culture.",
            f"Top-notch facilities and resources for {research_area} research. Professor is very supportive and encouraging.",
            f"Fantastic lab with world-class research in {research_area}. Lots of opportunities for collaboration and growth."
        ]

        # Neutral review templates
        neutral_templates = [
            f"Solid lab for {research_area} research. Good resources but mentorship could be more consistent.",
            f"Decent experience overall. Research projects in {research_area} are interesting but can be challenging.",
            f"The lab has good potential in {research_area} but work-life balance varies depending on deadlines.",
            f"Mixed experience. Great technical resources for {research_area} but communication could be improved."
        ]

        # Negative review templates
        negative_templates = [
            f"Challenging environment. While {research_area} research is cutting-edge, mentorship is inconsistent.",
            f"High-pressure lab with limited work-life balance. {research_area} projects are interesting but demanding.",
            f"Research quality in {research_area} is good but lab culture can be competitive and stressful.",
            f"Technical resources are adequate but mentorship and guidance in {research_area} could be better."
        ]

        # Select template based on rating
        if rating >= 4.0:
            review_text = positive_templates[review_index % len(positive_templates)]
            pros = self.get_positive_pros(research_area)
            cons = self.get_minor_cons()
        elif rating >= 3.0:
            review_text = neutral_templates[review_index % len(neutral_templates)]
            pros = self.get_mixed_pros(research_area)
            cons = self.get_moderate_cons()
        else:
            review_text = negative_templates[review_index % len(negative_templates)]
            pros = self.get_limited_pros(research_area)
            cons = self.get_major_cons()

        return {
            'text': review_text,
            'pros': pros,
            'cons': cons
        }

    def get_positive_pros(self, research_area):
        """Get pros for highly rated labs"""
        base_pros = [
            "Excellent mentorship and guidance",
            "Cutting-edge research opportunities",
            "Great work-life balance",
            "Strong collaboration culture"
        ]
        area_specific = {
            'AI': ["State-of-the-art AI infrastructure", "Access to large datasets"],
            'Machine Learning': ["Advanced computing resources", "Strong industry connections"],
            'Robotics': ["Excellent lab facilities", "Access to latest hardware"],
            'Computer Vision': ["High-quality datasets", "Advanced visualization tools"],
            'Natural Language Processing': ["Large language model access", "Diverse linguistic resources"],
            'Security': ["Real-world security challenges", "Industry partnerships"],
            'Systems': ["High-performance computing clusters", "Cloud infrastructure access"]
        }

        pros = base_pros[:3]  # Take first 3 base pros
        if research_area in area_specific:
            pros.extend(area_specific[research_area][:2])

        return pros

    def get_mixed_pros(self, research_area):
        """Get pros for moderately rated labs"""
        return [
            "Interesting research projects",
            "Adequate resources and facilities",
            "Opportunities for learning",
            "Decent technical support"
        ]

    def get_limited_pros(self, research_area):
        """Get pros for lower rated labs"""
        return [
            "Access to research projects",
            "Some learning opportunities",
            "Basic technical resources"
        ]

    def get_minor_cons(self):
        """Get minor cons for good labs"""
        return [
            "Can be competitive at times",
            "High expectations for performance"
        ]

    def get_moderate_cons(self):
        """Get moderate cons for average labs"""
        return [
            "Inconsistent mentorship quality",
            "Work-life balance varies by project",
            "Limited funding for conference travel"
        ]

    def get_major_cons(self):
        """Get major cons for poor labs"""
        return [
            "Poor work-life balance",
            "Limited mentorship and guidance",
            "Inadequate resources for research",
            "High stress environment"
        ]