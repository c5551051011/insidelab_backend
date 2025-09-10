#!/usr/bin/env python
"""
Populate test data for the insidelab backend
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from apps.universities.models import University, Professor
from apps.labs.models import Lab, RecruitmentStatus, ResearchTopic, Publication
from apps.reviews.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_data():
    print("Creating test data...")
    
    # Create Universities
    stanford = University.objects.create(
        name="Stanford University",
        country="USA",
        state="California",
        city="Stanford",
        website="https://stanford.edu",
        ranking=2
    )
    
    mit = University.objects.create(
        name="MIT",
        country="USA", 
        state="Massachusetts",
        city="Cambridge",
        website="https://mit.edu",
        ranking=1
    )
    
    berkeley = University.objects.create(
        name="UC Berkeley",
        country="USA",
        state="California", 
        city="Berkeley",
        website="https://berkeley.edu",
        ranking=4
    )
    
    # Create Professors
    feifei = Professor.objects.create(
        name="Dr. Fei-Fei Li",
        email="feifeili@cs.stanford.edu",
        university=stanford,
        department="Computer Science",
        research_interests=["Computer Vision", "AI Safety", "Deep Learning"]
    )
    
    regina = Professor.objects.create(
        name="Dr. Regina Barzilay", 
        email="regina@csail.mit.edu",
        university=mit,
        department="EECS",
        research_interests=["NLP", "Machine Learning", "Healthcare AI"]
    )
    
    pieter = Professor.objects.create(
        name="Dr. Pieter Abbeel",
        email="pabbeel@berkeley.edu", 
        university=berkeley,
        department="EECS",
        research_interests=["Robotics", "Reinforcement Learning", "Deep Learning"]
    )
    
    # Create Labs
    stanford_ai_lab = Lab.objects.create(
        name="Stanford AI Lab (SAIL)",
        professor=feifei,
        university=stanford,
        department="Computer Science",
        description="Leading AI research lab focusing on computer vision and AI safety with strong industry connections.",
        website="https://ai.stanford.edu/",
        lab_size=45,
        research_areas=["Computer Vision", "AI Safety", "Deep Learning"],
        tags=["Well Funded", "Industry Focus", "Publication Heavy"],
        overall_rating=4.6,
        review_count=128
    )
    
    mit_csail = Lab.objects.create(
        name="MIT CSAIL",
        professor=regina,
        university=mit,
        department="EECS", 
        description="Cutting-edge research in NLP and healthcare AI with focus on real-world impact.",
        website="https://www.csail.mit.edu/",
        lab_size=32,
        research_areas=["NLP", "Machine Learning", "Healthcare AI"],
        tags=["Top Tier", "Collaborative", "Innovation Focused"],
        overall_rating=4.7,
        review_count=156
    )
    
    bair = Lab.objects.create(
        name="Berkeley AI Research Lab (BAIR)",
        professor=pieter,
        university=berkeley,
        department="EECS",
        description="Premier robotics and RL lab with strong startup connections and industry impact.",
        website="https://bair.berkeley.edu/",
        lab_size=38, 
        research_areas=["Robotics", "Reinforcement Learning", "Deep Learning"],
        tags=["Startup Culture", "Well Funded", "Industry Focus"],
        overall_rating=4.8,
        review_count=142
    )
    
    # Create Recruitment Status
    RecruitmentStatus.objects.create(
        lab=stanford_ai_lab,
        is_recruiting_phd=True,
        is_recruiting_postdoc=True,
        is_recruiting_intern=False,
        notes="Actively recruiting PhD students in computer vision and robotics"
    )
    
    RecruitmentStatus.objects.create(
        lab=mit_csail,
        is_recruiting_phd=False,
        is_recruiting_postdoc=True,
        is_recruiting_intern=True,
        notes="No PhD openings this year, but accepting exceptional postdocs"
    )
    
    RecruitmentStatus.objects.create(
        lab=bair,
        is_recruiting_phd=True,
        is_recruiting_postdoc=False,
        is_recruiting_intern=True,
        notes="Looking for PhD students with robotics background"
    )
    
    # Create some test users
    user1 = User.objects.create_user(
        username="john_phd",
        email="john@stanford.edu",
        password="testpass123",
        name="John Smith",
        position="PhD Student",
        university=stanford,
        department="Computer Science"
    )
    
    user2 = User.objects.create_user(
        username="jane_ms",
        email="jane@mit.edu", 
        password="testpass123",
        name="Jane Doe",
        position="MS Student",
        university=mit,
        department="EECS"
    )
    
    # Create some test reviews
    Review.objects.create(
        lab=stanford_ai_lab,
        user=user1,
        position="PhD Student",
        duration="2 years",
        rating=4.5,
        category_ratings={
            "Mentorship Quality": 4.5,
            "Research Environment": 4.8,
            "Work-Life Balance": 3.9,
            "Career Support": 4.7,
            "Funding & Resources": 4.9,
            "Collaboration Culture": 4.4
        },
        review_text="Excellent research environment with world-class facilities. Professor Li is very supportive and gives great guidance. The lab has strong industry connections which helped with internships.",
        pros=["World-class research", "Great mentorship", "Industry connections", "Well funded"],
        cons=["Can be competitive", "High expectations"]
    )
    
    Review.objects.create(
        lab=mit_csail,
        user=user2,
        position="MS Student", 
        duration="1 year",
        rating=4.6,
        category_ratings={
            "Mentorship Quality": 4.8,
            "Research Environment": 4.9,
            "Work-Life Balance": 4.2,
            "Career Support": 4.6,
            "Funding & Resources": 4.8,
            "Collaboration Culture": 4.7
        },
        review_text="Amazing collaborative environment. The lab is at the forefront of NLP research and healthcare AI. Great opportunities for interdisciplinary work.",
        pros=["Cutting-edge research", "Collaborative culture", "Interdisciplinary opportunities"],
        cons=["Very demanding", "Long hours during deadlines"]
    )
    
    print("✅ Test data created successfully!")
    print(f"Created {University.objects.count()} universities")
    print(f"Created {Professor.objects.count()} professors")
    print(f"Created {Lab.objects.count()} labs")
    print(f"Created {User.objects.count()} users")
    print(f"Created {Review.objects.count()} reviews")

if __name__ == "__main__":
    create_test_data()