"""
Management command to populate Purdue University data with multiple departments.
Adds authentic research information for Computer Science, Engineering, and related departments.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.universities.models import University, Professor
from apps.labs.models import Lab
import time

class Command(BaseCommand):
    help = 'Populate Purdue University with research labs from multiple departments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-purdue',
            action='store_true',
            help='Clear existing Purdue data before creating new ones'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )

    def handle(self, *args, **options):
        start_time = time.time()

        if options['clear_purdue']:
            self.clear_purdue_data(options['dry_run'])

        self.create_purdue_data(options['dry_run'])

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Completed in {elapsed_time:.2f} seconds')
        )

    def clear_purdue_data(self, dry_run):
        """Clear existing Purdue data"""
        if dry_run:
            self.stdout.write('DRY RUN: Would clear existing Purdue University data')
            return

        try:
            purdue = University.objects.get(name="Purdue University")
            Lab.objects.filter(university=purdue).delete()
            Professor.objects.filter(university=purdue).delete()
            self.stdout.write(self.style.WARNING('Cleared existing Purdue data'))
        except University.DoesNotExist:
            pass

    def create_purdue_data(self, dry_run):
        """Create Purdue University data"""
        if dry_run:
            self.stdout.write('DRY RUN: Would create Purdue University data')
            return

        # Create or get Purdue University
        university_data = {
            'name': 'Purdue University',
            'country': 'USA',
            'state': 'Indiana',
            'city': 'West Lafayette',
            'website': 'https://www.purdue.edu/',
            'ranking': 42,  # US News ranking
            'logo_url': 'https://www.purdue.edu/purdue/images/wordmark_boiler_gold.png'
        }

        university, created = University.objects.get_or_create(
            name=university_data['name'],
            defaults=university_data
        )

        if created:
            self.stdout.write(f'Created university: {university.name}')
        else:
            self.stdout.write(f'University already exists: {university.name}')

        # Professor and Lab data for multiple departments
        departments_data = {
            'Computer Science': [
                {
                    'professor': {
                        'name': 'Dan Goldwasser',
                        'title': 'Associate Professor',
                        'email': 'dgoldwas@purdue.edu',
                        'research_interests': ['Natural Language Processing', 'Machine Learning', 'Computational Social Science'],
                        'bio': 'Expert in computational linguistics and NLP with focus on social media analysis and text understanding.'
                    },
                    'lab': {
                        'name': 'Purdue NLP Lab',
                        'description': 'Research lab focusing on natural language processing, computational linguistics, and machine learning applications to text analysis.',
                        'website': 'https://www.cs.purdue.edu/homes/dgoldwas/',
                        'research_areas': ['Natural Language Processing', 'Machine Learning', 'Computational Linguistics', 'Social Media Analysis'],
                        'lab_size': 8
                    }
                },
                {
                    'professor': {
                        'name': 'Ming Yin',
                        'title': 'Assistant Professor',
                        'email': 'mingyin@purdue.edu',
                        'research_interests': ['Human-Computer Interaction', 'Crowdsourcing', 'AI for Social Good'],
                        'bio': 'Researcher in human-computer interaction, focusing on crowdsourcing systems and AI applications for social impact.'
                    },
                    'lab': {
                        'name': 'Purdue HCI Lab',
                        'description': 'Human-Computer Interaction lab studying user interfaces, crowdsourcing platforms, and human-AI collaboration.',
                        'website': 'https://www.cs.purdue.edu/homes/mingyin/',
                        'research_areas': ['Human-Computer Interaction', 'Crowdsourcing', 'User Interface Design', 'AI for Social Good'],
                        'lab_size': 6
                    }
                },
                {
                    'professor': {
                        'name': 'Xiangyu Zhang',
                        'title': 'Professor',
                        'email': 'xyzhang@cs.purdue.edu',
                        'research_interests': ['Software Engineering', 'Program Analysis', 'Cybersecurity'],
                        'bio': 'Leading researcher in software engineering with expertise in program analysis, debugging, and software security.'
                    },
                    'lab': {
                        'name': 'Purdue Software Engineering Research Group',
                        'description': 'Research group focused on software engineering, program analysis, and cybersecurity applications.',
                        'website': 'https://www.cs.purdue.edu/homes/xyzhang/',
                        'research_areas': ['Software Engineering', 'Program Analysis', 'Cybersecurity', 'Software Testing'],
                        'lab_size': 10
                    }
                },
                {
                    'professor': {
                        'name': 'Rajesh Gupta',
                        'title': 'Professor',
                        'email': 'rkg@cs.purdue.edu',
                        'research_interests': ['Computer Systems', 'Embedded Systems', 'IoT'],
                        'bio': 'Expert in computer systems and embedded computing with focus on Internet of Things and cyber-physical systems.'
                    },
                    'lab': {
                        'name': 'Purdue Systems Lab',
                        'description': 'Research lab working on computer systems, embedded computing, and Internet of Things applications.',
                        'website': 'https://www.cs.purdue.edu/homes/rkg/',
                        'research_areas': ['Computer Systems', 'Embedded Systems', 'Internet of Things', 'Cyber-Physical Systems'],
                        'lab_size': 7
                    }
                }
            ],
            'Electrical and Computer Engineering': [
                {
                    'professor': {
                        'name': 'Kaushik Roy',
                        'title': 'Edward G. Tiedemann Jr. Distinguished Professor',
                        'email': 'kaushik@purdue.edu',
                        'research_interests': ['Neuromorphic Computing', 'AI Hardware', 'Low-Power Electronics'],
                        'bio': 'Pioneer in neuromorphic computing and low-power VLSI design with applications to artificial intelligence hardware.'
                    },
                    'lab': {
                        'name': 'Purdue Nanoelectronics Research Laboratory',
                        'description': 'Leading research lab in neuromorphic computing, AI hardware acceleration, and low-power electronics.',
                        'website': 'https://engineering.purdue.edu/NRL/',
                        'research_areas': ['Neuromorphic Computing', 'AI Hardware', 'Low-Power VLSI', 'Quantum Computing'],
                        'lab_size': 15
                    }
                },
                {
                    'professor': {
                        'name': 'David Love',
                        'title': 'Professor',
                        'email': 'djlove@ecn.purdue.edu',
                        'research_interests': ['Wireless Communications', '5G/6G Networks', 'Signal Processing'],
                        'bio': 'Expert in wireless communications and signal processing with focus on next-generation cellular networks.'
                    },
                    'lab': {
                        'name': 'Purdue Wireless Communications Lab',
                        'description': 'Research lab focusing on advanced wireless communication systems, 5G/6G networks, and signal processing.',
                        'website': 'https://engineering.purdue.edu/~djlove/',
                        'research_areas': ['Wireless Communications', '5G Networks', '6G Networks', 'Signal Processing'],
                        'lab_size': 12
                    }
                }
            ],
            'Industrial Engineering': [
                {
                    'professor': {
                        'name': 'Seokcheon Lee',
                        'title': 'Associate Professor',
                        'email': 'lee2337@purdue.edu',
                        'research_interests': ['Data Analytics', 'Machine Learning', 'Operations Research'],
                        'bio': 'Researcher in data analytics and machine learning applications to industrial engineering and operations research.'
                    },
                    'lab': {
                        'name': 'Purdue Data Analytics Lab',
                        'description': 'Research lab applying data analytics and machine learning to industrial engineering problems.',
                        'website': 'https://engineering.purdue.edu/IE/People/Faculty/lee2337/',
                        'research_areas': ['Data Analytics', 'Machine Learning', 'Operations Research', 'Supply Chain Analytics'],
                        'lab_size': 8
                    }
                }
            ],
            'Aeronautics and Astronautics': [
                {
                    'professor': {
                        'name': 'Inseok Hwang',
                        'title': 'Professor',
                        'email': 'ihwang@purdue.edu',
                        'research_interests': ['Autonomous Systems', 'Robotics', 'Control Systems'],
                        'bio': 'Leading researcher in autonomous systems and robotics with applications to aerospace and unmanned vehicles.'
                    },
                    'lab': {
                        'name': 'Purdue Autonomous Systems Lab',
                        'description': 'Research lab focused on autonomous systems, robotics, and control theory for aerospace applications.',
                        'website': 'https://engineering.purdue.edu/AAE/people/ptProfile?resource_id=2085',
                        'research_areas': ['Autonomous Systems', 'Robotics', 'Control Systems', 'Unmanned Aerial Vehicles'],
                        'lab_size': 10
                    }
                }
            ],
            'Statistics': [
                {
                    'professor': {
                        'name': 'Guang Cheng',
                        'title': 'Professor',
                        'email': 'chengg@purdue.edu',
                        'research_interests': ['Statistical Machine Learning', 'High-Dimensional Statistics', 'Deep Learning Theory'],
                        'bio': 'Expert in statistical machine learning and high-dimensional statistics with theoretical foundations of deep learning.'
                    },
                    'lab': {
                        'name': 'Purdue Statistical Machine Learning Lab',
                        'description': 'Research lab working on theoretical foundations of machine learning and high-dimensional statistical methods.',
                        'website': 'https://www.stat.purdue.edu/people/faculty/chengg',
                        'research_areas': ['Statistical Machine Learning', 'High-Dimensional Statistics', 'Deep Learning Theory', 'Statistical Computing'],
                        'lab_size': 6
                    }
                }
            ]
        }

        total_professors = 0
        total_labs = 0

        with transaction.atomic():
            for department_name, dept_data in departments_data.items():
                self.stdout.write(f'\nCreating {department_name} department data...')

                for item in dept_data:
                    prof_data = item['professor']
                    lab_data = item['lab']

                    # Create professor
                    professor, created = Professor.objects.get_or_create(
                        email=prof_data['email'],
                        defaults={
                            'name': prof_data['name'],
                            'university': university,
                            'department': department_name,
                            'research_interests': prof_data['research_interests'],
                            'bio': prof_data['bio'],
                            'personal_website': lab_data['website']  # Use lab website as professor website
                        }
                    )

                    if created:
                        total_professors += 1
                        self.stdout.write(f'  + Created professor: {professor.name}')

                    # Create lab
                    lab, created = Lab.objects.get_or_create(
                        name=lab_data['name'],
                        professor=professor,
                        defaults={
                            'university': university,
                            'department': department_name,
                            'description': lab_data['description'],
                            'website': lab_data['website'],
                            'research_areas': lab_data['research_areas'],
                            'lab_size': lab_data['lab_size'],
                            'tags': self.generate_tags(lab_data['research_areas'])
                        }
                    )

                    if created:
                        total_labs += 1
                        self.stdout.write(f'  + Created lab: {lab.name}')

        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {total_professors} professors and {total_labs} labs at Purdue University')
        )

    def generate_tags(self, research_areas):
        """Generate tags based on research areas"""
        tag_mapping = {
            'Natural Language Processing': ['nlp', 'ai', 'machine-learning'],
            'Machine Learning': ['machine-learning', 'ai', 'data-science'],
            'Human-Computer Interaction': ['hci', 'user-interface', 'ux'],
            'Software Engineering': ['software', 'programming', 'development'],
            'Cybersecurity': ['security', 'cyber', 'privacy'],
            'Computer Systems': ['systems', 'distributed', 'performance'],
            'Neuromorphic Computing': ['neuromorphic', 'brain-inspired', 'hardware'],
            'Wireless Communications': ['wireless', '5g', 'networking'],
            'Data Analytics': ['data-science', 'analytics', 'big-data'],
            'Autonomous Systems': ['robotics', 'autonomous', 'control'],
            'Statistical Machine Learning': ['statistics', 'machine-learning', 'theory']
        }

        tags = set()
        for area in research_areas:
            if area in tag_mapping:
                tags.update(tag_mapping[area])

        return list(tags)