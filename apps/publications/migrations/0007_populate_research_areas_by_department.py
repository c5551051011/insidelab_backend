# Migration to populate research areas by department

from django.db import migrations


def create_research_areas(apps, schema_editor):
    """Create sample research areas for each department"""
    ResearchArea = apps.get_model('publications', 'ResearchArea')
    Department = apps.get_model('universities', 'Department')

    # Research areas by department
    research_areas_data = {
        'Computer Science': [
            # AI/ML
            {'name': 'Artificial Intelligence', 'description': 'Machine learning, deep learning, neural networks'},
            {'name': 'Machine Learning', 'description': 'Statistical learning, pattern recognition, data mining'},
            {'name': 'Deep Learning', 'description': 'Neural networks, convolutional networks, transformer models'},
            {'name': 'Natural Language Processing', 'description': 'Text processing, language models, computational linguistics'},
            {'name': 'Computer Vision', 'description': 'Image processing, object detection, visual recognition'},
            {'name': 'Robotics', 'description': 'Autonomous systems, robot control, perception'},

            # Systems
            {'name': 'Operating Systems', 'description': 'Kernel design, distributed systems, virtualization'},
            {'name': 'Computer Networks', 'description': 'Network protocols, distributed computing, IoT'},
            {'name': 'Database Systems', 'description': 'Data management, query optimization, distributed databases'},
            {'name': 'Distributed Systems', 'description': 'Parallel computing, cloud computing, microservices'},
            {'name': 'Computer Architecture', 'description': 'Processor design, memory systems, parallel architectures'},

            # Security
            {'name': 'Cybersecurity', 'description': 'Network security, cryptography, security protocols'},
            {'name': 'Information Security', 'description': 'Data protection, privacy, access control'},
            {'name': 'Software Security', 'description': 'Secure coding, vulnerability analysis, malware detection'},

            # Software Engineering
            {'name': 'Software Engineering', 'description': 'Software development methodologies, testing, maintenance'},
            {'name': 'Programming Languages', 'description': 'Language design, compilers, type systems'},
            {'name': 'Human-Computer Interaction', 'description': 'User interface design, usability, user experience'},

            # Theory
            {'name': 'Algorithms', 'description': 'Algorithm design, complexity analysis, optimization'},
            {'name': 'Data Structures', 'description': 'Data organization, abstract data types, algorithm efficiency'},
            {'name': 'Computational Theory', 'description': 'Computational complexity, formal methods, automata theory'},
        ],

        'Electrical Engineering': [
            # Circuits & Electronics
            {'name': 'Circuit Design', 'description': 'Analog and digital circuit design, VLSI'},
            {'name': 'VLSI Design', 'description': 'Very large scale integration, chip design, semiconductor devices'},
            {'name': 'Microelectronics', 'description': 'Semiconductor devices, integrated circuits, nanoelectronics'},
            {'name': 'Power Electronics', 'description': 'Power conversion, motor drives, renewable energy systems'},

            # Communications
            {'name': 'Wireless Communications', 'description': '5G/6G, antenna design, RF systems'},
            {'name': 'Signal Processing', 'description': 'Digital signal processing, image processing, audio processing'},
            {'name': 'Communication Systems', 'description': 'Network protocols, modulation, coding theory'},
            {'name': 'Optical Communications', 'description': 'Fiber optics, photonic devices, optical networks'},

            # Control & Systems
            {'name': 'Control Systems', 'description': 'Automatic control, system identification, robust control'},
            {'name': 'Embedded Systems', 'description': 'Real-time systems, IoT devices, firmware development'},
            {'name': 'Robotics Control', 'description': 'Robot control algorithms, autonomous navigation, manipulation'},

            # Energy & Power
            {'name': 'Power Systems', 'description': 'Electrical power generation, transmission, smart grids'},
            {'name': 'Renewable Energy', 'description': 'Solar, wind, battery systems, energy storage'},
            {'name': 'Smart Grid', 'description': 'Grid modernization, energy management, demand response'},
        ],

        'Industrial Engineering': [
            # Operations Research
            {'name': 'Operations Research', 'description': 'Mathematical optimization, linear programming, simulation'},
            {'name': 'Supply Chain Management', 'description': 'Logistics, inventory management, procurement'},
            {'name': 'Quality Control', 'description': 'Statistical quality control, Six Sigma, process improvement'},
            {'name': 'Production Planning', 'description': 'Manufacturing systems, scheduling, capacity planning'},

            # Data Analytics
            {'name': 'Data Analytics', 'description': 'Business intelligence, predictive analytics, data mining'},
            {'name': 'Statistics', 'description': 'Statistical analysis, experimental design, hypothesis testing'},
            {'name': 'Decision Science', 'description': 'Decision theory, multi-criteria analysis, risk assessment'},

            # Human Factors
            {'name': 'Human Factors Engineering', 'description': 'Ergonomics, workplace design, human-machine interaction'},
            {'name': 'Systems Engineering', 'description': 'Complex systems design, requirements engineering, lifecycle management'},
            {'name': 'Project Management', 'description': 'Project planning, resource allocation, risk management'},
        ],

        'Artificial Intelligence': [
            # Core AI
            {'name': 'Machine Learning', 'description': 'Supervised/unsupervised learning, reinforcement learning'},
            {'name': 'Deep Learning', 'description': 'Neural networks, CNNs, RNNs, transformers'},
            {'name': 'Computer Vision', 'description': 'Image recognition, object detection, image generation'},
            {'name': 'Natural Language Processing', 'description': 'Language models, text analysis, machine translation'},
            {'name': 'Reinforcement Learning', 'description': 'Agent-based learning, policy optimization, game theory'},

            # Applied AI
            {'name': 'AI Ethics', 'description': 'Responsible AI, fairness, bias detection, explainable AI'},
            {'name': 'Autonomous Systems', 'description': 'Self-driving cars, drones, autonomous navigation'},
            {'name': 'Knowledge Representation', 'description': 'Ontologies, semantic web, expert systems'},
            {'name': 'AI for Healthcare', 'description': 'Medical imaging, drug discovery, clinical decision support'},
            {'name': 'AI for Finance', 'description': 'Algorithmic trading, fraud detection, risk assessment'},
        ],

        'Robotics engineering': [
            # Core Robotics
            {'name': 'Robot Control', 'description': 'Motion control, trajectory planning, dynamic modeling'},
            {'name': 'Robot Perception', 'description': 'Sensor fusion, SLAM, computer vision for robotics'},
            {'name': 'Robot Manipulation', 'description': 'Grasping, manipulation planning, dexterous hands'},
            {'name': 'Autonomous Navigation', 'description': 'Path planning, obstacle avoidance, localization'},

            # Applications
            {'name': 'Medical Robotics', 'description': 'Surgical robots, rehabilitation robotics, prosthetics'},
            {'name': 'Industrial Robotics', 'description': 'Manufacturing automation, assembly robots, quality inspection'},
            {'name': 'Service Robotics', 'description': 'Home robots, delivery robots, elderly care robotics'},
            {'name': 'Swarm Robotics', 'description': 'Multi-robot systems, collective intelligence, coordination'},

            # Technology
            {'name': 'Robot Learning', 'description': 'Learning from demonstration, adaptive control, skill acquisition'},
            {'name': 'Human-Robot Interaction', 'description': 'Social robotics, collaborative robots, robot communication'},
        ],

        'Mathematics': [
            # Pure Mathematics
            {'name': 'Abstract Algebra', 'description': 'Group theory, ring theory, field theory'},
            {'name': 'Real Analysis', 'description': 'Measure theory, functional analysis, topology'},
            {'name': 'Number Theory', 'description': 'Prime numbers, cryptographic applications, algebraic number theory'},
            {'name': 'Differential Geometry', 'description': 'Manifolds, Riemannian geometry, geometric analysis'},
            {'name': 'Topology', 'description': 'Algebraic topology, differential topology, knot theory'},

            # Applied Mathematics
            {'name': 'Mathematical Modeling', 'description': 'Differential equations, dynamical systems, simulation'},
            {'name': 'Optimization', 'description': 'Linear programming, convex optimization, numerical methods'},
            {'name': 'Statistics', 'description': 'Probability theory, statistical inference, Bayesian statistics'},
            {'name': 'Computational Mathematics', 'description': 'Numerical analysis, scientific computing, algorithms'},
            {'name': 'Mathematical Biology', 'description': 'Population dynamics, epidemiology, bioinformatics'},
        ],

        'Physics': [
            # Theoretical Physics
            {'name': 'Quantum Mechanics', 'description': 'Quantum theory, quantum field theory, quantum information'},
            {'name': 'Relativity', 'description': 'General relativity, cosmology, black holes'},
            {'name': 'Statistical Mechanics', 'description': 'Thermodynamics, phase transitions, critical phenomena'},
            {'name': 'Particle Physics', 'description': 'Elementary particles, standard model, high energy physics'},
            {'name': 'Condensed Matter Theory', 'description': 'Many-body systems, superconductivity, quantum materials'},

            # Experimental Physics
            {'name': 'Atomic Physics', 'description': 'Laser spectroscopy, cold atoms, precision measurements'},
            {'name': 'Optical Physics', 'description': 'Laser physics, nonlinear optics, quantum optics'},
            {'name': 'Solid State Physics', 'description': 'Crystal structure, electronic properties, materials science'},
            {'name': 'Nuclear Physics', 'description': 'Nuclear structure, radioactivity, nuclear reactions'},

            # Applied Physics
            {'name': 'Medical Physics', 'description': 'Radiation therapy, medical imaging, health physics'},
            {'name': 'Plasma Physics', 'description': 'Fusion energy, space plasmas, plasma applications'},
            {'name': 'Biophysics', 'description': 'Biological systems, protein dynamics, molecular motors'},
        ]
    }

    # Create research areas for each department
    for dept_name, areas in research_areas_data.items():
        try:
            department = Department.objects.get(name=dept_name)
            for area_data in areas:
                ResearchArea.objects.get_or_create(
                    name=area_data['name'],
                    department=department,
                    defaults={
                        'description': area_data['description'],
                        'color_code': '#3498db'
                    }
                )
        except Department.DoesNotExist:
            # Skip if department doesn't exist
            continue


def reverse_create_research_areas(apps, schema_editor):
    """Remove all research areas created by this migration"""
    ResearchArea = apps.get_model('publications', 'ResearchArea')
    ResearchArea.objects.filter(department__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0006_add_department_to_research_area'),
        ('universities', '0007_merge_20251030_1034'),
    ]

    operations = [
        migrations.RunPython(
            create_research_areas,
            reverse_create_research_areas
        ),
    ]