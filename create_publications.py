#!/usr/bin/env python3
"""
Script to create publications using Django ORM directly
Usage: python create_publications.py
"""

import os
import sys
import django
import json
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings.development')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

# Import models after Django setup
from django.db import transaction
from apps.publications.models import (
    Publication, Author, Venue, ResearchArea,
    PublicationAuthor, PublicationVenue, PublicationResearchArea
)
from apps.labs.models import Lab

# Publication data
publications_data = [
{
    "title": "Physics-informed Neural Mapping and Motion Planning in Unknown Environments",
    "publication_year": 2025,
    "abstract": "",
    "publication_date": "2025-01-01",
    "doi": "",
    "arxiv_id": "2410.09883",
    "citation_count": 0,
    "keywords": ["motion planning", "neural networks", "physics-informed learning", "robotics"],
    "additional_notes": "",
    "paper_url": "https://arxiv.org/pdf/2410.09883",
    "code_url": "",
    "video_url": "https://www.youtube.com/watch?v=qTPL5a6pRKk",
    "dataset_url": "",
    "slides_url": "",
    "is_open_access": True,
    "language": "en",
    "page_count": 0,
    "lab_id": 3,
    "authors": [
        {"name": "Yuchen Liu", "order": 1, "is_first_author": True},
        {"name": "Ruiqi Ni", "order": 2},
        {"name": "Ahmed H. Qureshi", "order": 3, "is_corresponding": True}
    ],
    "venues": [{"short_name": "T-RO", "type": "journal", "tier": "top"}],
    "research_areas": ["Robotics", "Motion Planning", "Physics-informed Learning"]
},
{
    "title": "DeRi-IGP: Learning to Manipulate Rigid Objects Using Deformable Linear Objects via Iterative Grasp-Pull",
    "publication_year": 2025,
    "abstract": "",
    "publication_date": "2025-01-01",
    "doi": "",
    "arxiv_id": "2309.04843",
    "citation_count": 0,
    "keywords": ["manipulation", "deformable objects", "robotics"],
    "additional_notes": "",
    "paper_url": "https://arxiv.org/pdf/2309.04843",
    "code_url": "",
    "video_url": "https://www.youtube.com/watch?v=j1rPA3qIqlU",
    "dataset_url": "",
    "slides_url": "",
    "is_open_access": True,
    "language": "en",
    "page_count": 0,
    "lab_id": 3,
    "authors": [
        {"name": "Zixing Wang", "order": 1, "is_first_author": True},
        {"name": "Ahmed H. Qureshi", "order": 2, "is_corresponding": True}
    ],
    "venues": [{"short_name": "RA-L", "type": "journal", "tier": "top"}],
    "research_areas": ["Robotics", "Object Manipulation"]
},
{
    "title": "Integrating Active Sensing and Rearrangement Planning for Efficient Object Retrieval from Unknown, Confined, Cluttered Environments",
    "publication_year": 2025,
    "abstract": "",
    "publication_date": "2025-05-01",
    "doi": "",
    "arxiv_id": "2411.11733",
    "citation_count": 0,
    "keywords": ["robot navigation", "motion planning", "object rearrangement", "robotics"],
    "additional_notes": "",
    "paper_url": "https://arxiv.org/pdf/2411.11733",
    "code_url": "",
    "video_url": "https://www.youtube.com/watch?v=tea7I-3RtV0",
    "dataset_url": "",
    "slides_url": "",
    "is_open_access": True,
    "language": "en",
    "page_count": 0,
    "lab_id": 3,
    "authors": [
        {"name": "Hanwen Ren", "order": 1, "is_first_author": True},
        {"name": "Junyoung Kim", "order": 2},
        {"name": "Ahmed H. Qureshi", "order": 3, "is_corresponding": True}
    ],
    "venues": [{"short_name": "ICRA", "type": "conference", "tier": "top"}],
    "research_areas": ["Robotics", "Motion Planning"]
},
{
    "title": "Physics-informed Temporal Difference Metric Learning for Robot Motion Planning",
    "publication_year": 2025,
    "abstract": "",
    "publication_date": "2025-04-01",
    "doi": "",
    "arxiv_id": "",
    "citation_count": 0,
    "keywords": ["motion planning", "deep learning", "physics-informed learning", "robotics"],
    "additional_notes": "",
    "paper_url": "https://openreview.net/forum?id=TOiageVNru",
    "code_url": "",
    "video_url": "",
    "dataset_url": "",
    "slides_url": "",
    "is_open_access": True,
    "language": "en",
    "page_count": 0,
    "lab_id": 3,
    "authors": [
        {"name": "Ruiqi Ni", "order": 1, "is_first_author": True},
        {"name": "Zehrong Pan", "order": 2},
        {"name": "Ahmed H. Qureshi", "order": 3, "is_corresponding": True}
    ],
    "venues": [{"short_name": "ICLR", "type": "conference", "tier": "top"}],
    "research_areas": ["Robotics", "Machine Learning", "Motion Planning"]
},
{
    "title": "Physics-informed Neural Motion Planning on Constraint Manifolds",
    "publication_year": 2024,
    "abstract": "",
    "publication_date": "2024-05-01",
    "doi": "",
    "arxiv_id": "2403.05765",
    "citation_count": 0,
    "keywords": ["motion planning", "neural networks", "physics-informed learning", "robotics"],
    "additional_notes": "",
    "paper_url": "https://arxiv.org/pdf/2403.05765",
    "code_url": "",
    "video_url": "https://youtu.be/qVhi7Pz3zjA?si=FI7h_jUYT2ZJLs38",
    "dataset_url": "",
    "slides_url": "",
    "is_open_access": True,
    "language": "en",
    "page_count": 0,
    "lab_id": 3,
    "authors": [
        {"name": "Ruiqi Ni", "order": 1, "is_first_author": True},
        {"name": "Ahmed H. Qureshi", "order": 2, "is_corresponding": True}
    ],
    "venues": [{"short_name": "ICRA", "type": "conference", "tier": "top"}],
    "research_areas": ["Robotics", "Motion Planning"]
}]

def create_publication(data):
    """Create a single publication with all related data"""
    try:
        with transaction.atomic():
            print(f"Creating: {data['title'][:60]}...")

            # 1. Create publication
            publication_data = {
                'title': data['title'],
                'publication_year': data['publication_year'],
                'abstract': data.get('abstract', ''),
                'doi': data.get('doi', ''),
                'arxiv_id': data.get('arxiv_id', ''),
                'citation_count': data.get('citation_count', 0),
                'keywords': data.get('keywords', []),
                'additional_notes': data.get('additional_notes', ''),
                'paper_url': data.get('paper_url', ''),
                'code_url': data.get('code_url', ''),
                'video_url': data.get('video_url', ''),
                'dataset_url': data.get('dataset_url', ''),
                'slides_url': data.get('slides_url', ''),
                'is_open_access': data.get('is_open_access', False),
                'language': data.get('language', 'en'),
                'page_count': data.get('page_count', 0),
            }

            if data.get('publication_date'):
                publication_data['publication_date'] = datetime.strptime(
                    data['publication_date'], '%Y-%m-%d'
                ).date()

            publication = Publication.objects.create(**publication_data)

            # 2. Connect to lab
            if data.get('lab_id'):
                try:
                    lab = Lab.objects.get(id=data['lab_id'])
                    publication.labs.add(lab)
                    print(f"  - Connected to lab: {lab.name}")
                except Lab.DoesNotExist:
                    print(f"  - Warning: Lab {data['lab_id']} not found")

            # 3. Create authors
            for i, author_data in enumerate(data.get('authors', [])):
                author_name = author_data.get('name')
                if not author_name:
                    continue

                author, created = Author.objects.get_or_create(
                    name=author_name,
                    defaults={'current_affiliation': ''}
                )

                PublicationAuthor.objects.create(
                    publication=publication,
                    author=author,
                    author_order=author_data.get('order', i + 1),
                    is_first_author=author_data.get('is_first_author', False),
                    is_corresponding=author_data.get('is_corresponding', False),
                    affiliation=''
                )

                if created:
                    print(f"  - Created author: {author_name}")
                else:
                    print(f"  - Found author: {author_name}")

            # 4. Create venues
            for venue_data in data.get('venues', []):
                venue_name = venue_data.get('name', venue_data.get('short_name', ''))
                if not venue_name:
                    continue

                venue, created = Venue.objects.get_or_create(
                    short_name=venue_data.get('short_name', ''),
                    defaults={
                        'name': venue_name,
                        'type': venue_data.get('type', 'conference'),
                        'tier': venue_data.get('tier', 'unknown'),
                    }
                )

                PublicationVenue.objects.create(
                    publication=publication,
                    venue=venue,
                    is_best_paper=venue_data.get('is_best_paper', False),
                    award_name=venue_data.get('award_name', ''),
                )

                if created:
                    print(f"  - Created venue: {venue.short_name}")
                else:
                    print(f"  - Found venue: {venue.short_name}")

            # 5. Create research areas
            for area_name in data.get('research_areas', []):
                area, created = ResearchArea.objects.get_or_create(
                    name=area_name,
                    defaults={'description': f'{area_name} research area'}
                )

                PublicationResearchArea.objects.create(
                    publication=publication,
                    research_area=area,
                    relevance_score=1.0
                )

                if created:
                    print(f"  - Created research area: {area_name}")
                else:
                    print(f"  - Found research area: {area_name}")

            print(f"  ✅ Successfully created publication: {publication.id}")
            return publication

    except Exception as e:
        print(f"  ❌ Error creating publication: {str(e)}")
        return None

def main():
    """Create all publications"""
    print("=== Creating Publications ===")
    print(f"Total publications to create: {len(publications_data)}")
    print()

    created_count = 0
    failed_count = 0

    for i, pub_data in enumerate(publications_data, 1):
        print(f"[{i}/{len(publications_data)}]")
        result = create_publication(pub_data)

        if result:
            created_count += 1
        else:
            failed_count += 1
        print()

    print("=== Summary ===")
    print(f"Successfully created: {created_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(publications_data)}")

if __name__ == '__main__':
    main()