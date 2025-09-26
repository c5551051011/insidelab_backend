"""
Management command to populate database with elite university data.
Includes MIT, Stanford, Carnegie Mellon, UC Berkeley, Harvard, Princeton, and Cornell.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.universities.models import University, Professor
from apps.labs.models import Lab
import time


class Command(BaseCommand):
    help = 'Populate database with elite university data (MIT, Stanford, CMU, Berkeley, Harvard, Princeton, Cornell)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )
        parser.add_argument(
            '--university',
            type=str,
            choices=['mit', 'stanford', 'cmu', 'berkeley', 'harvard', 'princeton', 'cornell', 'all'],
            default='all',
            help='Populate specific university only'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )

    def handle(self, *args, **options):
        start_time = time.time()

        if options['clear']:
            self.clear_data(options['dry_run'])

        if options['university'] == 'all':
            self.populate_all_universities(options['dry_run'])
        else:
            self.populate_university(options['university'], options['dry_run'])

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Completed in {elapsed_time:.2f} seconds')
        )

    def clear_data(self, dry_run):
        """Clear existing university data"""
        if dry_run:
            self.stdout.write('DRY RUN: Would clear existing data')
            return

        with transaction.atomic():
            # Clear in order to respect foreign key constraints
            Lab.objects.all().delete()
            Professor.objects.all().delete()
            University.objects.all().delete()

        self.stdout.write(self.style.WARNING('Cleared existing university data'))

    def populate_all_universities(self, dry_run):
        """Populate all universities"""
        universities = ['mit', 'stanford', 'cmu', 'berkeley', 'harvard', 'princeton', 'cornell']

        for uni in universities:
            self.populate_university(uni, dry_run)

    def populate_university(self, university_code, dry_run):
        """Populate specific university"""
        data_map = {
            'mit': self.get_mit_data,
            'stanford': self.get_stanford_data,
            'cmu': self.get_cmu_data,
            'berkeley': self.get_berkeley_data,
            'harvard': self.get_harvard_data,
            'princeton': self.get_princeton_data,
            'cornell': self.get_cornell_data
        }

        if university_code not in data_map:
            self.stdout.write(self.style.ERROR(f'Unknown university: {university_code}'))
            return

        data = data_map[university_code]()

        if dry_run:
            self.stdout.write(f'DRY RUN: Would create {data["name"]}')
            self.stdout.write(f'  - {len(data["labs"])} labs')
            total_professors = sum(len(lab["professors"]) for lab in data["labs"])
            self.stdout.write(f'  - {total_professors} professors')
            return

        self.create_university_data(data)

    def create_university_data(self, data):
        """Create university, labs, and professors"""
        with transaction.atomic():
            # Parse location for University model fields
            location_parts = data['location'].split(', ')
            if len(location_parts) >= 3:
                city = location_parts[0]
                state = location_parts[1]
                country = location_parts[2]
            else:
                city = data['location']
                state = ''
                country = 'United States'

            # Create university
            university, created = University.objects.get_or_create(
                name=data['name'],
                defaults={
                    'city': city,
                    'state': state,
                    'country': country,
                    'website': data['website']
                }
            )

            if created:
                self.stdout.write(f'Created university: {university.name}')
            else:
                self.stdout.write(f'University already exists: {university.name}')

            # Create labs and professors
            for lab_data in data['labs']:
                # First create the professor (since Lab model requires professor)
                main_professor = None
                for prof_data in lab_data['professors']:
                    professor, prof_created = Professor.objects.get_or_create(
                        name=prof_data['name'],
                        university=university,
                        defaults={
                            'department': 'Computer Science',  # Default department
                            'research_interests': prof_data['research_areas'].split(', ') if isinstance(prof_data['research_areas'], str) else [prof_data['research_areas']],
                            'bio': prof_data['bio'],
                            'personal_website': prof_data.get('website', ''),
                            'email': prof_data.get('email', '')
                        }
                    )

                    if prof_created:
                        self.stdout.write(f'    - Created professor: {professor.name}')

                    if main_professor is None:
                        main_professor = professor

                # Create lab with the main professor
                if main_professor:
                    lab, lab_created = Lab.objects.get_or_create(
                        name=lab_data['name'],
                        university=university,
                        professor=main_professor,
                        defaults={
                            'description': lab_data['description'],
                            'research_areas': lab_data['research_areas'],
                            'website': lab_data.get('website', ''),
                            'department': 'Computer Science'
                        }
                    )

                    if lab_created:
                        self.stdout.write(f'  + Created lab: {lab.name}')

        self.stdout.write(self.style.SUCCESS(f'✓ Populated {data["name"]}'))

    def get_mit_data(self):
        return {
            'name': 'Massachusetts Institute of Technology',
            'location': 'Cambridge, Massachusetts, United States',
            'description': 'MIT is a private research university founded in 1861, renowned for its cutting-edge research in science, technology, engineering, and mathematics. MIT\'s Computer Science and Artificial Intelligence Laboratory (CSAIL) is one of the world\'s most important centers of information technology research.',
            'website': 'https://www.mit.edu',
            'labs': [
                {
                    'name': 'Distributed Robotics Laboratory',
                    'description': 'Develops the science of autonomy for robots and AI systems integrated into everyday life, focusing on computational design and fabrication of robots, algorithms for perception, planning and control, and collaborative robotics.',
                    'research_areas': ['Distributed Robotics', 'Mobile Computing', 'Programmable Matter', 'Autonomous Vehicles', 'Soft Robotics'],
                    'professors': [{
                        'name': 'Daniela Rus',
                        'title': 'Andrew (1956) and Erna Viterbi Professor of Electrical Engineering and Computer Science, Director of CSAIL',
                        'research_areas': 'Distributed robotics, mobile computing, programmable matter, autonomous vehicles, soft robotics, swarm robotics',
                        'bio': 'Leading researcher in robotics with focus on making robots that can work alongside humans in complex environments. Her work spans autonomous vehicles, soft robotics, and swarm robotics systems.'
                    }]
                },
                {
                    'name': 'Learning and Intelligent Systems Group',
                    'description': 'Interdisciplinary research aimed at discovering principles underlying artificially intelligent robots that can perform everyday tasks, bringing together motion planning, machine learning, reinforcement learning, and computer vision.',
                    'research_areas': ['Machine Learning', 'Robotics', 'Reinforcement Learning', 'Decision Making', 'Motion Planning'],
                    'professors': [{
                        'name': 'Leslie Pack Kaelbling',
                        'title': 'Professor of Computer Science and Engineering',
                        'research_areas': 'Learning in robotics, decision-making under uncertainty, integrated task and motion planning',
                        'bio': 'Expert in artificial intelligence and robotics, focusing on algorithms that enable robots to learn and adapt to complex, uncertain environments.'
                    }]
                },
                {
                    'name': 'Interactive Robotics Group',
                    'description': 'Designs models and algorithms that enable robots to infer human cognitive state and learn from human team members, developing algorithms for human-machine teaming.',
                    'research_areas': ['Human-Robot Interaction', 'Team Coordination', 'Manufacturing', 'Healthcare Robotics'],
                    'professors': [{
                        'name': 'Julie Shah',
                        'title': 'Professor of Aeronautics and Astronautics',
                        'research_areas': 'Human-robot interaction, work team coordination, manufacturing assembly lines, healthcare robotics',
                        'bio': 'Researcher focusing on developing AI systems that can collaborate effectively with human teams in manufacturing, healthcare, and other complex domains.'
                    }]
                },
                {
                    'name': 'Computer Graphics Group',
                    'description': 'Creates cutting-edge research in computer graphics, computational photography, and digital fabrication, connecting images and computation.',
                    'research_areas': ['Computer Graphics', 'Digital Fabrication', 'Computational Photography', '3D Printing'],
                    'professors': [
                        {
                            'name': 'Wojciech Matusik',
                            'title': 'Professor of Electrical Engineering and Computer Science',
                            'research_areas': 'Computer graphics, digital fabrication, computational design, 3D printing',
                            'bio': 'Leader of the Computational Design and Fabrication Group, named one of the world\'s top 100 young innovators by MIT\'s Technology Review Magazine in 2004.'
                        },
                        {
                            'name': 'Fredo Durand',
                            'title': 'Professor of Computer Science',
                            'research_areas': 'Computer graphics, computational photography, human perception, visual computing',
                            'bio': 'Renowned researcher in computer graphics with over 56,000 citations, focusing on image and video generation, photography, and visual perception technologies.'
                        }
                    ]
                },
                {
                    'name': 'Computer Vision Group',
                    'description': 'Creates state-of-the-art systems for object, people, scene, and behavior recognition with applications in healthcare, gaming, and tagging systems.',
                    'research_areas': ['Computer Vision', 'Machine Learning', 'Scene Understanding', 'Neural Networks'],
                    'professors': [{
                        'name': 'Antonio Torralba',
                        'title': 'Professor of Electrical Engineering and Computer Science',
                        'research_areas': 'Computer vision, machine learning, scene understanding, neural networks',
                        'bio': 'Leading researcher in computer vision and machine learning, known for work on scene understanding, neural radiance fields, and large-scale visual recognition systems.'
                    }]
                },
                {
                    'name': 'Machine Learning Group',
                    'description': 'Studies machine learning applications for robotics, healthcare, language processing, and information retrieval, including precision medicine, motion planning, and computer vision.',
                    'research_areas': ['Machine Learning', 'Healthcare AI', 'Natural Language Processing', 'Cancer Detection'],
                    'professors': [{
                        'name': 'Regina Barzilay',
                        'title': 'School of Engineering Distinguished Professor for AI and Health',
                        'research_areas': 'Natural language processing, machine learning for healthcare, AI for cancer detection and drug discovery',
                        'bio': 'Renowned for pioneering work in natural language processing and its applications to medicine, developing AI systems for cancer detection and pharmaceutical research.'
                    }]
                },
                {
                    'name': 'Cryptography and Information Security Group',
                    'description': 'Develops techniques for securing global information infrastructure through theoretical foundations, practical applications, and speculative research in cryptography and security.',
                    'research_areas': ['Cryptography', 'Computer Security', 'RSA Encryption', 'Zero-Knowledge Proofs'],
                    'professors': [
                        {
                            'name': 'Ron Rivest',
                            'title': 'Institute Professor',
                            'research_areas': 'Cryptography, computer security, algorithms, RSA encryption',
                            'bio': 'Co-inventor of the RSA algorithm and creator of RC2, RC4, RC5 encryption algorithms and MD5 hash function. Recipient of the 2002 ACM Turing Award.'
                        },
                        {
                            'name': 'Shafi Goldwasser',
                            'title': 'RSA Professor of Electrical Engineering and Computer Science',
                            'research_areas': 'Cryptography, computational complexity, zero-knowledge proofs, interactive proofs',
                            'bio': 'Pioneer in modern cryptography, co-recipient of the 2013 ACM Turing Award for transforming cryptography from an art into a science.'
                        }
                    ]
                }
            ]
        }

    def get_stanford_data(self):
        return {
            'name': 'Stanford University',
            'location': 'Stanford, California, United States',
            'description': 'Stanford University is a leading research university committed to promoting the public welfare through teaching, learning, and research. With over 36 Nobel Prize winners and strong ties to Silicon Valley, Stanford continues to be at the forefront of technological and scientific advancement.',
            'website': 'https://www.stanford.edu',
            'labs': [
                {
                    'name': 'Stanford Artificial Intelligence Laboratory (SAIL)',
                    'description': 'SAIL has been a center of excellence for Artificial Intelligence research for over 60 years, focusing on biomedicine, computational cognitive science, computer vision, and human-centered AI.',
                    'research_areas': ['AI', 'Machine Learning', 'Computer Vision', 'Natural Language Processing', 'Robotics'],
                    'professors': [{
                        'name': 'Fei-Fei Li',
                        'title': 'Sequoia Capital Professor, Co-Director Stanford Institute for Human-Centered AI',
                        'research_areas': 'Computer vision, artificial intelligence, machine learning applications in healthcare',
                        'bio': 'Elected Member of the National Academy of Engineering and Medicine, recipient of the VinFuture Prize (2024), and a leading figure in computer vision research.'
                    }]
                },
                {
                    'name': 'Stanford Natural Language Processing Group',
                    'description': 'A leading research group focused on robust linguistically sophisticated natural language understanding and generation, with emphasis on compositionality, question answering, and large language models.',
                    'research_areas': ['Natural Language Processing', 'Computational Linguistics', 'Deep Learning for NLP'],
                    'professors': [
                        {
                            'name': 'Christopher Manning',
                            'title': 'Thomas M. Siebel Professor in Machine Learning, Departments of Linguistics and Computer Science',
                            'research_areas': 'Natural language understanding and generation, deep learning for NLP, compositionality, question answering, large language models',
                            'bio': 'Co-author of the widely-used textbook "Speech and Language Processing" and founder of the Stanford NLP group.'
                        },
                        {
                            'name': 'Dan Jurafsky',
                            'title': 'Professor and Chair of Linguistics, Professor of Computer Science',
                            'research_areas': 'Computational linguistics, natural language understanding, human-human conversation, speech processing',
                            'bio': 'Recipient of a 2002 MacArthur Fellowship, co-author of "Speech and Language Processing" textbook.'
                        }
                    ]
                },
                {
                    'name': 'Stanford Vision and Learning Lab (SVL)',
                    'description': 'Tackles fundamental open problems in computer vision research and develops visual functionalities that give rise to semantically meaningful interpretations of the visual world.',
                    'research_areas': ['Computer Vision', 'Machine Learning', 'Visual Understanding'],
                    'professors': [{
                        'name': 'Percy Liang',
                        'title': 'Associate Professor of Computer Science',
                        'research_areas': 'Foundation models, machine learning, natural language processing, robustness, interpretability',
                        'bio': 'Director of the Center for Research on Foundation Models, focused on making foundation models more accessible and understandable.'
                    }]
                },
                {
                    'name': 'Stanford Robotics Laboratory',
                    'description': 'Focuses on novel control architectures, algorithms, sensing, and human-friendly designs for advanced robotic capabilities in complex environments.',
                    'research_areas': ['Robotics', 'Control Systems', 'Human-Robot Interaction', 'Haptic Technology'],
                    'professors': [{
                        'name': 'Oussama Khatib',
                        'title': 'Professor of Computer Science, Director of Robotics Laboratory',
                        'research_areas': 'Robotics control, human-robot interaction, haptic technology, biomechanics',
                        'bio': 'Member of the National Academy of Engineering, recipient of multiple IEEE awards including the Pioneering Award and Technical Field Award.'
                    }]
                },
                {
                    'name': 'Applied Cryptography Group',
                    'description': 'Focuses on applied cryptography research, developing cryptosystems with novel properties and security mechanisms for modern computing.',
                    'research_areas': ['Cryptography', 'Security', 'Privacy-Preserving Technologies'],
                    'professors': [{
                        'name': 'Dan Boneh',
                        'title': 'Professor of Computer Science and Electrical Engineering, Co-director of Computer Security Lab',
                        'research_areas': 'Applied cryptography, computer security, adversarial machine learning, quantum computing',
                        'bio': 'Recipient of the 2014 ACM Prize and 2013 Gödel Prize, elected to National Academy of Engineering in 2016.'
                    }]
                },
                {
                    'name': 'Stanford HCI Group',
                    'description': 'Studies human-computer interaction and the design of social computing systems, focusing on the intersection of technology and human behavior.',
                    'research_areas': ['Human-Computer Interaction', 'Social Computing Systems', 'Interactive Technologies'],
                    'professors': [{
                        'name': 'Michael Bernstein',
                        'title': 'Professor of Computer Science, Bass University Fellow',
                        'research_areas': 'Human-computer interaction, social computing systems, interactive technologies',
                        'bio': 'Senior Fellow at Stanford HAI, recipient of Alfred P. Sloan Fellowship and multiple best paper awards at top HCI conferences.'
                    }]
                }
            ]
        }

    def get_cmu_data(self):
        return {
            'name': 'Carnegie Mellon University',
            'location': 'Pittsburgh, Pennsylvania, United States',
            'description': 'Carnegie Mellon University is a global research university known for its world-class, interdisciplinary programs in technology, science, arts, business, and public policy. The School of Computer Science, established in 1988, was one of the first of its kind and consistently ranks #1 globally for AI and Computer Science.',
            'website': 'https://www.cmu.edu',
            'labs': [
                {
                    'name': 'Human-Computer Interaction Institute (HCII)',
                    'description': 'One of the world\'s largest HCI research institutes with 50+ faculty from diverse disciplines',
                    'research_areas': ['Human-centered computing', 'AI ethics', 'accessibility', 'learning technologies'],
                    'professors': [
                        {
                            'name': 'Brad Myers',
                            'title': 'Charles M. Geschke Director and Professor',
                            'research_areas': 'End-user software engineering, usable privacy and security',
                            'bio': 'Leading researcher in programming environments and user interface tools'
                        },
                        {
                            'name': 'Jodi Forlizzi',
                            'title': 'Herbert A. Simon Professor',
                            'research_areas': 'Interaction design, service design, design research methods',
                            'bio': 'Pioneer in experience design and human-centered AI'
                        }
                    ]
                },
                {
                    'name': 'Robotics Institute',
                    'description': 'Founded in 1979 as the first academic department dedicated to robotics research',
                    'research_areas': ['Field robotics', 'autonomous systems', 'computer vision', 'manipulation'],
                    'professors': [
                        {
                            'name': 'Red Whittaker',
                            'title': 'Fredkin Research Professor',
                            'research_areas': 'Field robotics, planetary exploration, autonomous vehicles',
                            'bio': 'Pioneer in field robotics who led teams in DARPA Grand Challenge competitions'
                        },
                        {
                            'name': 'Jun-Yan Zhu',
                            'title': 'Assistant Professor',
                            'research_areas': 'Computer graphics, computer vision, generative AI',
                            'bio': '2024 Samsung AI Researcher of the Year, expert in visual AI and generative models'
                        }
                    ]
                },
                {
                    'name': 'Machine Learning Department',
                    'description': 'World\'s first academic machine learning department (founded 2006), ranked #1 globally',
                    'research_areas': ['Deep learning', 'statistical learning', 'reinforcement learning', 'AI safety'],
                    'professors': [
                        {
                            'name': 'Aviral Kumar',
                            'title': 'Assistant Professor',
                            'research_areas': 'Reinforcement learning, offline RL, robotics',
                            'bio': '2024 Samsung AI Researcher of the Year, expert in learning from data'
                        },
                        {
                            'name': 'Yuanzhi Li',
                            'title': 'Assistant Professor',
                            'research_areas': 'Machine learning theory, optimization, deep learning',
                            'bio': 'Recent addition to faculty with expertise in theoretical foundations of ML'
                        }
                    ]
                },
                {
                    'name': 'Language Technologies Institute (LTI)',
                    'description': 'Leading institute in computational linguistics with 33 faculty members',
                    'research_areas': ['Natural language processing', 'speech processing', 'machine translation'],
                    'professors': [
                        {
                            'name': 'Mona Diab',
                            'title': 'Director and Professor',
                            'research_areas': 'Natural language processing, computational linguistics, multilingual AI',
                            'bio': 'Leading researcher in cross-lingual NLP and Arabic language technologies'
                        },
                        {
                            'name': 'Graham Neubig',
                            'title': 'Associate Professor',
                            'research_areas': 'Large language models, machine translation, code generation',
                            'bio': 'Director of NeuLab, expert in neural approaches to language processing'
                        }
                    ]
                },
                {
                    'name': 'CyLab Security & Privacy Institute',
                    'description': 'One of the largest university-based cybersecurity research centers in the US',
                    'research_areas': ['Cybersecurity', 'privacy', 'cryptography', 'secure systems'],
                    'professors': [{
                        'name': 'Lorrie Cranor',
                        'title': 'Director and FORE Systems Professor',
                        'research_areas': 'Usable privacy and security, human factors in security',
                        'bio': 'Leading expert in privacy technologies and human-computer interaction in security'
                    }]
                }
            ]
        }

    def get_berkeley_data(self):
        return {
            'name': 'University of California, Berkeley',
            'location': 'Berkeley, California, United States',
            'description': 'UC Berkeley is a leading public research university in the San Francisco Bay Area, renowned for its excellence in research and education. The Electrical Engineering and Computer Sciences (EECS) department is consistently ranked among the top programs worldwide.',
            'website': 'https://www.berkeley.edu',
            'labs': [
                {
                    'name': 'Berkeley Artificial Intelligence Research (BAIR) Lab',
                    'description': 'BAIR is UC Berkeley\'s flagship AI research lab, bringing together over 50 faculty and 300+ graduate students across multiple AI disciplines.',
                    'research_areas': ['AI', 'Machine Learning', 'Computer Vision', 'Robotics', 'Natural Language Processing'],
                    'professors': [
                        {
                            'name': 'Stuart Russell',
                            'title': 'Professor of Computer Science',
                            'research_areas': 'Artificial Intelligence, AI Safety, Human-Compatible AI, Knowledge Representation',
                            'bio': 'Leading AI researcher and co-author of "Artificial Intelligence: A Modern Approach," the standard textbook in AI. Pioneer in AI safety and value alignment research.'
                        },
                        {
                            'name': 'Pieter Abbeel',
                            'title': 'Professor of Computer Science, Co-Director of BAIR',
                            'research_areas': 'Deep Reinforcement Learning, Robotics, Imitation Learning, Meta-Learning',
                            'bio': 'World-leading researcher in AI and robotics, co-founder of Gradescope and Covariant. His students have co-founded over a dozen AI companies including OpenAI and Perplexity.'
                        }
                    ]
                },
                {
                    'name': 'Robotics and Intelligent Machines Lab (AUTOLAB)',
                    'description': 'Led by Ken Goldberg, focusing on robust robot grasping, manipulation, and applications in warehouses, homes, and robot-assisted surgery.',
                    'research_areas': ['Robotics', 'Automation', 'Cloud Robotics', 'Surgical Robotics'],
                    'professors': [
                        {
                            'name': 'Ken Goldberg',
                            'title': 'Professor of Industrial Engineering and Operations Research, William S. Floyd Jr. Distinguished Chair',
                            'research_areas': 'Robotics, Automation, Cloud Robotics, Medical Robotics',
                            'bio': 'Artist, writer, inventor, and robotics researcher. Created the first robot on the Internet (1994). Director of CITRIS "People and Robots" Initiative with 300+ publications.'
                        },
                        {
                            'name': 'Sergey Levine',
                            'title': 'Associate Professor of EECS',
                            'research_areas': 'Deep Reinforcement Learning, Robotics, Machine Learning for Control',
                            'bio': 'Expert in algorithms enabling autonomous agents to acquire complex behaviors through learning. Co-founder of Physical Intelligence and key contributor to modern deep RL methods.'
                        }
                    ]
                },
                {
                    'name': 'Computer Security Group',
                    'description': 'Leading research in computer security spanning theory to applications, with expertise in mobile security, cryptography, and privacy-preserving systems.',
                    'research_areas': ['Computer Security', 'Cryptography', 'Privacy', 'Systems Security'],
                    'professors': [
                        {
                            'name': 'Dawn Song',
                            'title': 'Professor of Computer Science',
                            'research_areas': 'Computer Security, Privacy, Applied Cryptography, Deep Learning Security, Blockchain',
                            'bio': 'MacArthur "Genius" Fellow focusing on security and privacy in systems, software, networking. Pioneer in AI security and blockchain research.'
                        },
                        {
                            'name': 'David Wagner',
                            'title': 'Professor of Computer Science, Carl J. Penther Chair in Engineering',
                            'research_areas': 'Computer Security, Cryptography, Mobile Security, Privacy',
                            'bio': 'Leading expert in computer security and cryptography. Co-designer of an AES candidate, extensive work on mobile security and vulnerability discovery in deployed systems.'
                        }
                    ]
                },
                {
                    'name': 'Machine Learning Theory Group',
                    'description': 'Fundamental research at the intersection of statistics, machine learning, and optimization.',
                    'research_areas': ['Statistical Learning Theory', 'Optimization', 'Probabilistic Models'],
                    'professors': [
                        {
                            'name': 'Michael Jordan',
                            'title': 'Pehong Chen Distinguished Professor (EECS and Statistics)',
                            'research_areas': 'Machine Learning, Statistics, Optimization, Bayesian Methods',
                            'bio': 'Named "most influential computer scientist" by Science magazine. Pioneer in Bayesian networks and variational methods, member of National Academy of Sciences.'
                        },
                        {
                            'name': 'Peter Bartlett',
                            'title': 'Professor of EECS and Statistics',
                            'research_areas': 'Machine Learning Theory, Statistical Learning, Neural Networks',
                            'bio': 'Leading theorist in statistical learning theory with fundamental contributions to understanding generalization in machine learning.'
                        }
                    ]
                },
                {
                    'name': 'Systems Research Group',
                    'description': 'Research in large-scale distributed systems, cloud computing, and networking infrastructure.',
                    'research_areas': ['Distributed Systems', 'Operating Systems', 'Networking', 'Cloud Computing'],
                    'professors': [
                        {
                            'name': 'Ion Stoica',
                            'title': 'Professor of EECS',
                            'research_areas': 'Distributed Systems, Cloud Computing, Networking',
                            'bio': 'Leading expert in distributed systems and cloud computing, co-founder of Databricks and Anyscale. Key contributor to Apache Spark ecosystem.'
                        },
                        {
                            'name': 'Scott Shenker',
                            'title': 'Professor of EECS',
                            'research_areas': 'Computer Networking, Distributed Systems, Internet Architecture',
                            'bio': 'Influential researcher in computer networking and internet architecture, with fundamental contributions to network design and protocols.'
                        }
                    ]
                }
            ]
        }

    def get_harvard_data(self):
        return {
            'name': 'Harvard University',
            'location': 'Cambridge, Massachusetts, United States',
            'description': 'Harvard University, established in 1636, is a prestigious private Ivy League research university. The John A. Paulson School of Engineering and Applied Sciences (SEAS) is home to world-class computer science and engineering research programs with a highly interdisciplinary approach.',
            'website': 'https://www.harvard.edu',
            'labs': [
                {
                    'name': 'Data to Actionable Knowledge (DtAK) Lab',
                    'description': 'Research focuses on probabilistic methods, interpretability, and decision-making under uncertainty, with applications in healthcare and human-AI interaction.',
                    'research_areas': ['Machine Learning', 'AI', 'Healthcare'],
                    'professors': [{
                        'name': 'Finale Doshi-Velez',
                        'title': 'Professor of Computer Science',
                        'research_areas': 'Machine learning, healthcare informatics, interpretability, probabilistic modeling, reinforcement learning',
                        'bio': 'Professor at Harvard SEAS and affiliate of Kempner Institute. Her work focuses on developing interpretable machine learning methods for healthcare applications.'
                    }]
                },
                {
                    'name': 'Harvard Microrobotics Laboratory',
                    'description': 'Focuses on mechanics, materials, design, and manufacturing for novel bioinspired, medical, origami, soft and underwater robots. Famous for the RoboBees project.',
                    'research_areas': ['Robotics', 'Bio-inspired Systems'],
                    'professors': [{
                        'name': 'Robert J. Wood',
                        'title': 'Harry Lewis and Marlyn McGrath Professor of Engineering and Applied Sciences',
                        'research_areas': 'Microrobotics, bio-inspired robots, soft materials, wearable robots, micro-manufacturing techniques',
                        'bio': 'Director of Harvard Microrobotics Laboratory and professor at SEAS and Wyss Institute. Pioneer in miniature flying robots and the RoboBees project.'
                    }]
                },
                {
                    'name': 'Harvard Biodesign Lab',
                    'description': 'Develops robots and smart medical devices for human interaction, focusing on soft exosuits, assistive devices, and minimally invasive medical tools.',
                    'research_areas': ['Robotics', 'Medical Devices', 'Wearable Technology'],
                    'professors': [{
                        'name': 'Conor J. Walsh',
                        'title': 'Paul A. Maeder Professor of Engineering and Applied Sciences',
                        'research_areas': 'Wearable robotics, soft robotics, rehabilitation engineering, human augmentation',
                        'bio': 'Founder of Harvard Biodesign Lab and associate faculty at Wyss Institute. Winner of multiple prestigious awards including Blavatnik National Award.'
                    }]
                },
                {
                    'name': 'Intelligent Interactive Systems Group',
                    'description': 'Research focuses on intelligent interactive systems that bridge AI and HCI, including accessible computing, behavioral research at scale, and design for equity.',
                    'research_areas': ['Human-Computer Interaction', 'AI'],
                    'professors': [{
                        'name': 'Krzysztof Z. Gajos',
                        'title': 'Yahn W. Bernier and N. Elizabeth McCaw Professor of Computer Science',
                        'research_areas': 'Human-computer interaction, intelligent user interfaces, accessible computing, social computing',
                        'bio': 'Professor at Harvard SEAS with PhD from University of Washington. Former editor-in-chief of ACM TiiS and general chair of ACM UIST 2017.'
                    }]
                },
                {
                    'name': 'Architecture, Circuits and Compilers Group',
                    'description': 'Research focuses on computer architecture, hardware-software co-design for AI systems, energy-efficient computing, and sustainable computing.',
                    'research_areas': ['Computer Systems', 'AI Hardware'],
                    'professors': [{
                        'name': 'David Brooks',
                        'title': 'Haley Family Professor of Computer Science',
                        'research_areas': 'Computer architecture, energy-efficient computing, AI hardware acceleration, hardware-software co-design',
                        'bio': 'Professor at Harvard SEAS and ACM/IEEE Fellow. Expert in power-efficient computer architectures with research adopted in commercial systems.'
                    }]
                }
            ]
        }

    def get_princeton_data(self):
        return {
            'name': 'Princeton University',
            'location': 'Princeton, New Jersey, United States',
            'description': 'Princeton University is a private Ivy League research university founded in 1746. Through teaching and research, Princeton educates people who will contribute to society and develop knowledge that will make a difference in the world.',
            'website': 'https://www.princeton.edu',
            'labs': [
                {
                    'name': 'Princeton Visual AI Lab',
                    'description': 'Develops artificially intelligent systems that reason about the visual world, integrating computer vision, machine learning, HCI, cognitive science, and fairness/accountability research.',
                    'research_areas': ['Computer Vision', 'Machine Learning', 'Human-Computer Interaction', 'AI Fairness'],
                    'professors': [{
                        'name': 'Olga Russakovsky',
                        'title': 'Associate Professor, Associate Director of Princeton Laboratory for Artificial Intelligence',
                        'research_areas': 'Computer vision, machine learning, human-computer interaction, AI fairness and accountability',
                        'bio': 'Lead author of ImageNet Large Scale Visual Recognition Challenge. Recipient of PECASE 2025, PAMI Young Researcher Award 2022, and MIT Technology Review\'s 35-under-35 Innovator 2017.'
                    }]
                },
                {
                    'name': 'Princeton Computational Imaging Lab',
                    'description': 'Explores imaging and computer vision approaches for super-human camera capabilities, including extreme environmental conditions, ultra-fast imaging, and next-generation optical computing systems.',
                    'research_areas': ['Computational Photography', 'Computer Vision', 'Optics', 'Machine Learning'],
                    'professors': [{
                        'name': 'Felix Heide',
                        'title': 'Assistant Professor',
                        'research_areas': 'Computational imaging, computer vision, optics, machine learning, robotics',
                        'bio': 'Develops next-generation imaging systems combining optics with AI. Recipient of SIGGRAPH Significant New Researcher, Sloan Fellowship, and Packard Fellowship.'
                    }]
                },
                {
                    'name': 'Princeton NLP Group',
                    'description': 'A leading research group focused on making computers understand and use human language effectively, with emphasis on training, adapting, and understanding large language models.',
                    'research_areas': ['Natural Language Processing', 'Large Language Models', 'Machine Learning'],
                    'professors': [
                        {
                            'name': 'Danqi Chen',
                            'title': 'Associate Professor, Co-Director Princeton NLP Group, Associate Director Princeton Language and Intelligence',
                            'research_areas': 'Deep learning for NLP, large language models, text understanding, knowledge representation',
                            'bio': 'Focus on making large language models more accessible to academia. Recipient of Sloan Fellowship, NSF CAREER award, Samsung AI Researcher of the Year.'
                        },
                        {
                            'name': 'Karthik Narasimhan',
                            'title': 'Associate Professor, Co-Director Princeton NLP Group, Head of Research at Sierra',
                            'research_areas': 'Natural language processing, reinforcement learning, autonomous agents',
                            'bio': 'Builds autonomous agents that learn through language and experience. Recipient of NSF CAREER Award, Google Research Scholar Award.'
                        }
                    ]
                },
                {
                    'name': 'Princeton Graphics Group',
                    'description': 'Research at the interface between computation and the physical world, including 3D scan acquisition, computational fabrication, appearance capture, and cultural heritage documentation.',
                    'research_areas': ['Computer Graphics', '3D Shape Analysis', 'Computational Fabrication', 'Robotics'],
                    'professors': [{
                        'name': 'Szymon Rusinkiewicz',
                        'title': 'David M. Siegel \'83 Professor of Computer Science, Department Chair',
                        'research_areas': 'Computer graphics, 3D shape acquisition, computational fabrication, robotics',
                        'bio': 'Research at interface of computation and physical world, including 3D scanning, appearance capture, and cultural heritage documentation. Highly cited (29,000+ citations).'
                    }]
                },
                {
                    'name': 'Princeton Privacy and Security Lab',
                    'description': 'Studies the societal impact of digital technologies, web privacy transparency, machine learning bias, and cryptocurrency systems.',
                    'research_areas': ['Web Privacy', 'AI Ethics', 'Data De-anonymization', 'Information Security'],
                    'professors': [{
                        'name': 'Arvind Narayanan',
                        'title': 'Professor, Director of Center for Information Technology Policy',
                        'research_areas': 'Web privacy, AI ethics, data de-anonymization, cryptocurrency, machine learning bias',
                        'bio': 'Led Princeton\'s Web Transparency and Accountability Project, co-authored cryptocurrency textbook used in 150+ courses. PECASE recipient, TIME 100 AI list.'
                    }]
                }
            ]
        }

    def get_cornell_data(self):
        return {
            'name': 'Cornell University',
            'location': 'Ithaca, New York, United States',
            'description': 'Cornell University is a private research university that provides exceptional education for undergraduates and graduate students. The Computer Science Department, part of the Cornell Ann S. Bowers College of Computing and Information Science, is consistently ranked among the best computer science departments in the U.S.',
            'website': 'https://www.cornell.edu',
            'labs': [
                {
                    'name': 'EmPRISE Lab (Empowering People through Robotics, Intelligent Systems, and Embodied AI)',
                    'description': 'Develops robotic technologies to assist people with motor disabilities, focusing on activities of daily living',
                    'research_areas': ['Assistive Robotics', 'Human-Robot Interaction', 'Robot Manipulation'],
                    'professors': [{
                        'name': 'Tapomayukh Bhattacharjee',
                        'title': 'Assistant Professor of Computer Science',
                        'research_areas': 'Assistive Robotics, Human-Robot Interaction, Haptic Perception, Robot Manipulation',
                        'bio': 'Director of the EmPRISE Lab, focuses on enabling robots to assist people with mobility limitations with activities of daily living.'
                    }]
                },
                {
                    'name': 'Cornell Graphics and Vision Group',
                    'description': 'Researches visual computing with applications in visual effects, animation, games, architecture, and photography',
                    'research_areas': ['Computer Graphics', 'Computer Vision', 'Rendering', 'Material Modeling'],
                    'professors': [
                        {
                            'name': 'Steve Marschner',
                            'title': 'Professor of Computer Science',
                            'research_areas': 'Computer Graphics, Realistic Rendering, Material Models, Appearance Capture',
                            'bio': '2015 ACM SIGGRAPH Computer Graphics Achievement Award winner. Revolutionized material modeling for hair, skin, wood, marble, and fabric.'
                        },
                        {
                            'name': 'Noah Snavely',
                            'title': 'Professor of Computer Science',
                            'research_areas': 'Computer Vision, 3D Scene Understanding, Structure from Motion, Computational Photography',
                            'bio': 'Professor at Cornell Tech and member of Cornell Graphics and Vision Group. PECASE recipient, Microsoft New Faculty Fellow, Alfred P. Sloan Fellow.'
                        }
                    ]
                },
                {
                    'name': 'Natural Language Processing Group',
                    'description': 'Develops computational models of human language and machine learning systems',
                    'research_areas': ['Natural Language Processing', 'Computational Linguistics', 'Machine Learning'],
                    'professors': [{
                        'name': 'Yoav Artzi',
                        'title': 'Associate Professor of Computer Science',
                        'research_areas': 'Natural language processing, machine learning, computational semantics',
                        'bio': 'Works on natural language understanding and machine learning, with focus on semantic parsing and grounded language understanding'
                    }]
                },
                {
                    'name': 'Cornell Theory Group',
                    'description': 'Studies efficient computation, computational processes, and their limits',
                    'research_areas': ['Theoretical Computer Science', 'Algorithms', 'Computational Complexity'],
                    'professors': [
                        {
                            'name': 'Jon Kleinberg',
                            'title': 'Professor of Computer Science',
                            'research_areas': 'Algorithms, Networks, Information Systems, Computational Social Science',
                            'bio': '2006 Rolf Nevanlinna Prize winner, 2001 NAS Award for Initiatives in Research recipient, Packard Fellow. Co-author of "Algorithm Design" textbook.'
                        },
                        {
                            'name': 'Eva Tardos',
                            'title': 'Jacob Gould Schurman Professor of Computer Science',
                            'research_areas': 'Algorithmic Game Theory, Network Economics, Algorithms, Optimization',
                            'bio': 'Former Department Chair, elected to American Academy of Arts & Sciences and National Academy of Engineering. George B. Dantzig Prize winner from SIAM.'
                        }
                    ]
                },
                {
                    'name': 'Initiative for CryptoCurrencies and Contracts (IC3)',
                    'description': 'Meets blockchain community\'s need for expertise in cryptography, distributed systems, and security',
                    'research_areas': ['Blockchain Technology', 'Cryptography', 'Security', 'Smart Contracts'],
                    'professors': [{
                        'name': 'Ari Juels',
                        'title': 'Weill Family Foundation and Joan and Sanford I. Weill Professor',
                        'research_areas': 'Blockchain Technology, Cryptography, Security, Privacy',
                        'bio': 'Co-director of IC3, former Chief Scientist at RSA and director of RSA Laboratories. Over 100 highly cited research papers. Chief Scientist at Chainlink Labs.'
                    }]
                }
            ]
        }