"""
Management command to populate lab recruitment status and recent publications.
Adds realistic recruitment status and publication data for all labs.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from apps.labs.models import Lab, RecruitmentStatus, Publication
import random
import time
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Populate recruitment status and recent publications for all labs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing recruitment status and publications before creating new ones'
        )
        parser.add_argument(
            '--publications-per-lab',
            type=int,
            default=3,
            help='Number of publications to create per lab (default: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )

    def handle(self, *args, **options):
        start_time = time.time()

        if options['clear_existing']:
            self.clear_existing_data(options['dry_run'])

        self.create_recruitment_status(options['dry_run'])
        self.create_publications(options['publications_per_lab'], options['dry_run'])

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Completed in {elapsed_time:.2f} seconds')
        )

    def clear_existing_data(self, dry_run):
        """Clear existing recruitment status and publications"""
        if dry_run:
            self.stdout.write('DRY RUN: Would clear existing recruitment status and publications')
            return

        with transaction.atomic():
            RecruitmentStatus.objects.all().delete()
            Publication.objects.all().delete()

        self.stdout.write(self.style.WARNING('Cleared existing recruitment status and publications'))

    def create_recruitment_status(self, dry_run):
        """Create recruitment status for all labs"""
        labs = Lab.objects.all()

        if dry_run:
            self.stdout.write(f'DRY RUN: Would create recruitment status for {labs.count()} labs')
            return

        created_count = 0

        for lab in labs:
            # Generate realistic recruitment status
            recruitment_data = self.generate_recruitment_status(lab)

            recruitment_status, created = RecruitmentStatus.objects.get_or_create(
                lab=lab,
                defaults=recruitment_data
            )

            if created:
                created_count += 1
                self.stdout.write(f'Created recruitment status for: {lab.name}')

        self.stdout.write(
            self.style.SUCCESS(f'✓ Created recruitment status for {created_count} labs')
        )

    def create_publications(self, publications_per_lab, dry_run):
        """Create recent publications for all labs"""
        labs = Lab.objects.all()

        if dry_run:
            self.stdout.write(f'DRY RUN: Would create {publications_per_lab} publications for {labs.count()} labs')
            return

        total_publications = 0

        for lab in labs:
            self.stdout.write(f'Creating publications for: {lab.name}')

            for i in range(publications_per_lab):
                publication_data = self.generate_publication_data(lab, i)

                publication = Publication.objects.create(
                    lab=lab,
                    **publication_data
                )

                total_publications += 1
                self.stdout.write(f'  + Created publication: {publication.title[:50]}...')

        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {total_publications} publications across {labs.count()} labs')
        )

    def generate_recruitment_status(self, lab):
        """Generate realistic recruitment status for a lab"""

        # Different recruitment patterns based on lab type and reputation
        lab_name_lower = lab.name.lower()

        # Top-tier labs are more selective
        is_top_tier = any(keyword in lab_name_lower for keyword in [
            'sail', 'bair', 'csail', 'mit', 'stanford ai', 'robotics institute'
        ])

        # AI/ML labs tend to recruit more actively
        is_ai_ml = any(keyword in lab_name_lower for keyword in [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural'
        ])

        # Generate recruitment probabilities
        if is_top_tier:
            phd_prob = 0.7  # High demand, selective
            postdoc_prob = 0.4
            intern_prob = 0.3  # Very competitive
        elif is_ai_ml:
            phd_prob = 0.8  # High demand field
            postdoc_prob = 0.6
            intern_prob = 0.7
        else:
            phd_prob = 0.6
            postdoc_prob = 0.5
            intern_prob = 0.6

        is_recruiting_phd = random.random() < phd_prob
        is_recruiting_postdoc = random.random() < postdoc_prob
        is_recruiting_intern = random.random() < intern_prob

        # Generate recruitment notes
        notes = self.generate_recruitment_notes(lab, is_recruiting_phd, is_recruiting_postdoc, is_recruiting_intern)

        return {
            'is_recruiting_phd': is_recruiting_phd,
            'is_recruiting_postdoc': is_recruiting_postdoc,
            'is_recruiting_intern': is_recruiting_intern,
            'notes': notes
        }

    def generate_recruitment_notes(self, lab, recruiting_phd, recruiting_postdoc, recruiting_intern):
        """Generate realistic recruitment notes"""

        research_area = lab.research_areas[0] if lab.research_areas else "computer science"
        notes = []

        if recruiting_phd:
            phd_requirements = [
                f"Actively recruiting PhD students in {research_area}.",
                f"Seeking PhD candidates with strong background in {research_area}.",
                f"PhD positions available in {research_area} research.",
                f"Looking for motivated PhD students interested in {research_area}."
            ]
            notes.append(random.choice(phd_requirements))

            # Add specific requirements
            requirements = [
                "Strong mathematical background required.",
                "Prior research experience preferred.",
                "Programming experience in Python/C++ expected.",
                "Strong publication record preferred.",
                "Excellent academic record required.",
                "Research experience in related areas valued."
            ]
            notes.append(random.choice(requirements))

        if recruiting_postdoc:
            postdoc_notes = [
                f"Postdoc positions available for researchers with expertise in {research_area}.",
                f"Seeking postdoctoral researchers with strong publication record in {research_area}.",
                f"Multiple postdoc openings in {research_area} projects.",
                f"Postdoc opportunities for researchers in {research_area}."
            ]
            notes.append(random.choice(postdoc_notes))

        if recruiting_intern:
            intern_notes = [
                "Summer internship positions available for qualified students.",
                "Competitive internship program for undergraduate and graduate students.",
                "Research internships available for students with relevant coursework.",
                "Limited internship spots available - early application recommended."
            ]
            notes.append(random.choice(intern_notes))

        if not (recruiting_phd or recruiting_postdoc or recruiting_intern):
            notes.append("Not currently recruiting. Check back next academic year for openings.")

        # Add application instructions
        if recruiting_phd or recruiting_postdoc:
            application_notes = [
                "Please contact the lab directly with your CV and research interests.",
                "Applications should include CV, research statement, and references.",
                "Interested candidates should email with CV and cover letter.",
                "Apply through university graduate admissions portal."
            ]
            notes.append(random.choice(application_notes))

        return " ".join(notes)

    def generate_publication_data(self, lab, pub_index):
        """Generate realistic publication data for a lab"""

        research_area = lab.research_areas[0] if lab.research_areas else "Computer Science"

        # Generate publication titles based on research area
        titles = self.get_publication_titles_by_area(research_area, pub_index)
        title = random.choice(titles)

        # Generate author list (professor + students/postdocs)
        authors = self.generate_author_list(lab)

        # Generate venue based on research area
        venue = self.get_venue_by_area(research_area)

        # Generate publication year (recent publications)
        year = random.choice([2024, 2024, 2023, 2023, 2022])  # Bias toward recent years

        # Generate realistic citation count
        citations = self.generate_citation_count(year)

        # Generate abstract
        abstract = self.generate_abstract(research_area, title)

        # Generate URL (some papers have URLs, some don't)
        url = self.generate_publication_url() if random.random() < 0.8 else ""

        return {
            'title': title,
            'authors': authors,
            'venue': venue,
            'year': year,
            'url': url,
            'abstract': abstract,
            'citations': citations
        }

    def get_publication_titles_by_area(self, research_area, index):
        """Get publication titles based on research area"""

        area_lower = research_area.lower()

        if 'ai' in area_lower or 'artificial intelligence' in area_lower:
            return [
                "Attention Is All You Need: Advances in Transformer Architecture",
                "Neural Architecture Search for Efficient Deep Learning Models",
                "Federated Learning with Differential Privacy Guarantees",
                "Self-Supervised Learning for Large-Scale Visual Representation",
                "Multimodal Learning with Cross-Attention Mechanisms",
                "Reinforcement Learning with Human Feedback at Scale"
            ]
        elif 'machine learning' in area_lower or 'deep learning' in area_lower:
            return [
                "Scalable Deep Learning with Distributed Training",
                "Meta-Learning for Few-Shot Classification Tasks",
                "Adversarial Training for Robust Neural Networks",
                "Continual Learning without Catastrophic Forgetting",
                "Efficient Neural Network Compression Techniques",
                "Bayesian Deep Learning for Uncertainty Quantification"
            ]
        elif 'robotics' in area_lower:
            return [
                "Robotic Manipulation with Deep Reinforcement Learning",
                "Real-Time SLAM for Autonomous Navigation Systems",
                "Learning Dexterous Manipulation from Human Demonstrations",
                "Soft Robotics for Safe Human-Robot Interaction",
                "Multi-Robot Coordination in Dynamic Environments",
                "Vision-Based Grasping with Tactile Feedback"
            ]
        elif 'computer vision' in area_lower or 'vision' in area_lower:
            return [
                "3D Scene Understanding from Single RGB Images",
                "Real-Time Object Detection with Efficient Architectures",
                "Neural Radiance Fields for Novel View Synthesis",
                "Semantic Segmentation with Transformer Networks",
                "Self-Supervised Learning for Visual Representation",
                "Video Understanding with Temporal Attention Models"
            ]
        elif 'nlp' in area_lower or 'natural language' in area_lower:
            return [
                "Large Language Models for Code Generation",
                "Multilingual Neural Machine Translation Systems",
                "Dialogue Systems with Contextual Understanding",
                "Information Extraction from Scientific Literature",
                "Question Answering with Retrieval-Augmented Generation",
                "Sentiment Analysis for Social Media Text"
            ]
        elif 'graphics' in area_lower:
            return [
                "Neural Rendering for Photorealistic Image Synthesis",
                "Real-Time Ray Tracing with Machine Learning Acceleration",
                "3D Shape Generation with Variational Autoencoders",
                "Physically-Based Animation with Deep Learning",
                "Texture Synthesis using Generative Adversarial Networks",
                "Virtual Reality Rendering Optimization Techniques"
            ]
        elif 'security' in area_lower or 'cryptography' in area_lower:
            return [
                "Privacy-Preserving Machine Learning with Homomorphic Encryption",
                "Blockchain Consensus Mechanisms for Scalability",
                "Adversarial Attacks on Deep Neural Networks",
                "Zero-Knowledge Proofs for Authenticated Data Structures",
                "Post-Quantum Cryptography Implementation",
                "Secure Multi-Party Computation in Distributed Systems"
            ]
        elif 'systems' in area_lower or 'distributed' in area_lower:
            return [
                "Scalable Distributed Storage Systems for Big Data",
                "Container Orchestration in Edge Computing Environments",
                "Real-Time Stream Processing with Low Latency",
                "Fault-Tolerant Distributed Consensus Algorithms",
                "Energy-Efficient Data Center Resource Management",
                "Serverless Computing Performance Optimization"
            ]
        elif 'hci' in area_lower or 'human-computer' in area_lower:
            return [
                "Adaptive User Interfaces for Accessibility",
                "Virtual Reality Interface Design for Productivity",
                "Eye-Tracking Based Interaction Techniques",
                "Voice User Interface Design for Smart Homes",
                "Haptic Feedback Systems for Remote Collaboration",
                "Augmented Reality Applications in Education"
            ]
        else:
            return [
                "Novel Algorithms for Computational Efficiency",
                "Theoretical Foundations of Modern Computing",
                "Optimization Techniques for Large-Scale Problems",
                "Data Structures for High-Performance Applications",
                "Algorithmic Approaches to Complex Systems",
                "Computational Complexity in Practical Applications"
            ]

    def generate_author_list(self, lab):
        """Generate realistic author list for a publication"""

        # Start with the lab's professor
        professor_name = lab.professor.name
        authors = [professor_name]

        # Add 1-4 additional authors (students, postdocs, collaborators)
        additional_authors = [
            "Sarah Chen", "Michael Rodriguez", "Emily Zhang", "David Kim",
            "Lisa Wang", "James Thompson", "Anna Patel", "Kevin Liu",
            "Maria Gonzalez", "Alex Johnson", "Jennifer Lee", "Robert Davis",
            "Amanda Wilson", "Daniel Chang", "Rachel Brown", "Steven Yang"
        ]

        num_additional = random.randint(1, 4)
        selected_authors = random.sample(additional_authors, num_additional)

        # Randomly place professor in author list (first, middle, or last)
        all_authors = selected_authors + [professor_name]
        random.shuffle(all_authors)

        return all_authors

    def get_venue_by_area(self, research_area):
        """Get realistic publication venue based on research area"""

        area_lower = research_area.lower()

        venues = {
            'ai': ['NeurIPS 2024', 'ICML 2024', 'AAAI 2024', 'IJCAI 2024', 'ICLR 2024'],
            'machine learning': ['NeurIPS 2024', 'ICML 2024', 'ICLR 2024', 'UAI 2024', 'AISTATS 2024'],
            'robotics': ['ICRA 2024', 'IROS 2024', 'RSS 2024', 'IEEE T-RO', 'IJRR'],
            'computer vision': ['CVPR 2024', 'ICCV 2023', 'ECCV 2024', 'IEEE TPAMI', 'IJCV'],
            'nlp': ['ACL 2024', 'EMNLP 2024', 'NAACL 2024', 'EACL 2024', 'CL Journal'],
            'graphics': ['SIGGRAPH 2024', 'SIGGRAPH Asia 2024', 'Eurographics 2024', 'IEEE TVCG', 'CGF'],
            'security': ['IEEE S&P 2024', 'CCS 2024', 'USENIX Security 2024', 'NDSS 2024', 'IEEE TDSC'],
            'systems': ['OSDI 2024', 'SOSP 2023', 'NSDI 2024', 'EuroSys 2024', 'IEEE TPDS'],
            'hci': ['CHI 2024', 'UIST 2024', 'UbiComp 2024', 'IEEE TVCG', 'IJHCS']
        }

        # Find matching venue category
        for category, venue_list in venues.items():
            if category in area_lower:
                return random.choice(venue_list)

        # Default venues for other areas
        default_venues = [
            'IEEE Computer', 'ACM Computing Surveys', 'Nature Machine Intelligence',
            'Science Robotics', 'Communications of the ACM', 'IEEE Computer'
        ]
        return random.choice(default_venues)

    def generate_citation_count(self, year):
        """Generate realistic citation count based on publication year"""

        current_year = 2024
        years_since_publication = current_year - year

        if years_since_publication == 0:  # 2024 papers
            return random.randint(0, 50)
        elif years_since_publication == 1:  # 2023 papers
            return random.randint(10, 200)
        elif years_since_publication == 2:  # 2022 papers
            return random.randint(25, 500)
        else:  # Older papers
            return random.randint(50, 1000)

    def generate_abstract(self, research_area, title):
        """Generate realistic abstract based on research area and title"""

        abstract_templates = {
            'problem': [
                f"Recent advances in {research_area} have shown promising results, but several challenges remain.",
                f"Existing approaches to {research_area} face significant limitations in scalability and efficiency.",
                f"The growing complexity of {research_area} applications requires novel computational approaches.",
                f"Current methods in {research_area} struggle with real-world deployment and robustness."
            ],
            'approach': [
                "We propose a novel framework that addresses these limitations through innovative algorithmic design.",
                "Our approach leverages deep learning techniques combined with traditional optimization methods.",
                "We introduce a new methodology that significantly improves upon state-of-the-art baselines.",
                "This work presents a comprehensive solution that integrates multiple complementary techniques."
            ],
            'results': [
                "Experimental results demonstrate substantial improvements over existing methods.",
                "Our evaluation shows significant performance gains across multiple benchmark datasets.",
                "Comprehensive experiments validate the effectiveness of our proposed approach.",
                "Results indicate promising applications in real-world scenarios with practical impact."
            ],
            'conclusion': [
                "These findings open new directions for future research in the field.",
                "The proposed method provides a solid foundation for practical applications.",
                "This work contributes to the theoretical understanding and practical advancement of the field.",
                "Our approach offers a scalable solution with broad applicability."
            ]
        }

        # Select one sentence from each category
        abstract_parts = []
        for category in ['problem', 'approach', 'results', 'conclusion']:
            abstract_parts.append(random.choice(abstract_templates[category]))

        return " ".join(abstract_parts)

    def generate_publication_url(self):
        """Generate realistic publication URL"""

        url_types = [
            "https://arxiv.org/abs/2024.{:05d}",
            "https://ieeexplore.ieee.org/document/{:06d}",
            "https://dl.acm.org/doi/10.1145/{}.{}",
            "https://proceedings.neurips.cc/paper/2024/hash/{}.html"
        ]

        url_template = random.choice(url_types)

        if "arxiv" in url_template:
            return url_template.format(random.randint(10000, 99999))
        elif "ieee" in url_template:
            return url_template.format(random.randint(100000, 999999))
        elif "acm" in url_template:
            return url_template.format(random.randint(3000000, 3999999), random.randint(3000000, 3999999))
        else:  # NeurIPS
            hash_val = ''.join(random.choices('abcdef0123456789', k=32))
            return url_template.format(hash_val)