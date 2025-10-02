# apps/publications/management/commands/load_publication_data.py
import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from apps.publications.models import (
    Publication, Author, Venue, ResearchArea,
    PublicationAuthor, PublicationVenue, PublicationResearchArea
)
from apps.labs.models import Lab


class Command(BaseCommand):
    help = 'Load publication data from JSON files in dataset folder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Specific JSON file to load (optional)',
        )
        parser.add_argument(
            '--dataset-dir',
            type=str,
            default='dataset',
            help='Directory containing JSON files (default: dataset)',
        )

    def handle(self, *args, **options):
        dataset_dir = options['dataset_dir']
        specific_file = options.get('file')

        if not os.path.exists(dataset_dir):
            self.stdout.write(
                self.style.ERROR(f'Dataset directory "{dataset_dir}" not found')
            )
            return

        # Get JSON files to process
        if specific_file:
            json_files = [specific_file] if specific_file.endswith('.json') else [f"{specific_file}.json"]
        else:
            json_files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]

        total_created = 0
        total_errors = 0

        for json_file in json_files:
            file_path = os.path.join(dataset_dir, json_file)

            if not os.path.exists(file_path):
                self.stdout.write(
                    self.style.WARNING(f'File not found: {file_path}')
                )
                continue

            self.stdout.write(f'Processing {json_file}...')

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    publications_data = json.load(f)

                created_count, error_count = self.process_publications(publications_data, json_file)
                total_created += created_count
                total_errors += error_count

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {json_file}: {created_count} publications created, {error_count} errors'
                    )
                )

            except json.JSONDecodeError as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Invalid JSON in {json_file}: {e}')
                )
                total_errors += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error processing {json_file}: {e}')
                )
                total_errors += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 SUMMARY: {total_created} publications created, {total_errors} errors'
            )
        )

    def process_publications(self, publications_data, filename):
        """Process a list of publications from JSON data"""
        created_count = 0
        error_count = 0

        for i, data in enumerate(publications_data):
            try:
                with transaction.atomic():
                    publication = self.create_publication_with_relations(data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✅ [{i+1}] "{publication.title[:50]}..."'
                        )
                    )
            except Exception as e:
                error_count += 1
                title = data.get('title', 'Unknown')[:50]
                self.stdout.write(
                    self.style.ERROR(
                        f'  ❌ [{i+1}] "{title}...": {str(e)}'
                    )
                )

        return created_count, error_count

    def create_publication_with_relations(self, data):
        """Create publication with all related data"""

        # 1. Create publication
        publication_data = {
            'title': data['title'],
            'publication_year': data['publication_year'],
            'abstract': data.get('abstract', ''),
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
            'page_count': data.get('page_count'),
        }

        # Handle unique fields - only set if not empty
        if data.get('doi') and data['doi'].strip():
            publication_data['doi'] = data['doi']
        if data.get('arxiv_id') and data['arxiv_id'].strip():
            publication_data['arxiv_id'] = data['arxiv_id']

        # Handle publication_date
        if data.get('publication_date'):
            try:
                publication_data['publication_date'] = datetime.strptime(
                    data['publication_date'], '%Y-%m-%d'
                ).date()
            except ValueError:
                # If date format is invalid, skip it
                pass

        publication = Publication.objects.create(**publication_data)

        # 2. Connect to labs
        lab_ids = data.get('lab_ids', [])
        if data.get('lab_id'):
            lab_ids.append(data['lab_id'])

        for lab_id in lab_ids:
            try:
                lab = Lab.objects.get(id=lab_id)
                publication.labs.add(lab)
            except Lab.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'    ⚠️  Lab with id {lab_id} not found')
                )

        # 3. Process authors
        authors_data = data.get('authors', [])
        for i, author_data in enumerate(authors_data):
            author_name = author_data.get('name')
            if not author_name:
                continue

            # Create or get author
            author_defaults = {
                'email': author_data.get('email', ''),
                'current_affiliation': author_data.get('affiliation', ''),
                'current_position': author_data.get('position', ''),
            }

            # Handle ORCID - only set if not empty
            if author_data.get('orcid') and author_data['orcid'].strip():
                author_defaults['orcid'] = author_data['orcid']

            author, created = Author.objects.get_or_create(
                name=author_name,
                defaults=author_defaults
            )

            # Create publication-author relationship
            PublicationAuthor.objects.create(
                publication=publication,
                author=author,
                author_order=author_data.get('order', i + 1),
                is_first_author=author_data.get('is_first_author', i == 0),
                is_corresponding=author_data.get('is_corresponding', False),
                is_last_author=author_data.get('is_last_author', False),
                affiliation=author_data.get('affiliation', ''),
                affiliation_lab_id=author_data.get('lab_id')
            )

        # 4. Process venues
        venues_data = data.get('venues', [])
        for venue_data in venues_data:
            venue_name = venue_data.get('name')
            if not venue_name:
                continue

            # Create or get venue
            venue, created = Venue.objects.get_or_create(
                name=venue_name,
                type=venue_data.get('type', 'conference'),
                defaults={
                    'short_name': venue_data.get('short_name', ''),
                    'tier': venue_data.get('tier', 'unknown'),
                    'field': venue_data.get('field', ''),
                }
            )

            # Create publication-venue relationship
            PublicationVenue.objects.create(
                publication=publication,
                venue=venue,
                presentation_type=venue_data.get('presentation_type', 'poster'),
                is_best_paper=venue_data.get('is_best_paper', False),
                is_best_student_paper=venue_data.get('is_best_student_paper', False),
                is_outstanding_paper=venue_data.get('is_outstanding_paper', False),
                award_name=venue_data.get('award_name', ''),
            )

        # 5. Process research areas
        research_areas = data.get('research_areas', [])
        for area_name in research_areas:
            area, created = ResearchArea.objects.get_or_create(
                name=area_name,
                defaults={'description': f'{area_name} 연구 분야'}
            )
            PublicationResearchArea.objects.create(
                publication=publication,
                research_area=area,
                relevance_score=1.0
            )

        return publication