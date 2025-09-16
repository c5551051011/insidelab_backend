"""
Management command to recalculate all precomputed averages.
Use this to populate initial data or fix inconsistencies.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.labs.models import Lab, LabCategoryAverage
from apps.reviews.models import RatingCategory
import time


class Command(BaseCommand):
    help = 'Recalculate all precomputed lab category averages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lab-id',
            type=int,
            help='Recalculate averages for a specific lab only'
        )
        parser.add_argument(
            '--category-id',
            type=int,
            help='Recalculate averages for a specific category across all labs'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Process labs in batches (default: 100)'
        )

    def handle(self, *args, **options):
        start_time = time.time()

        if options['lab_id']:
            self.recalculate_lab(options['lab_id'], options['dry_run'])
        elif options['category_id']:
            self.recalculate_category(options['category_id'], options['dry_run'])
        else:
            self.recalculate_all(options['dry_run'], options['batch_size'])

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f'Completed in {elapsed_time:.2f} seconds')
        )

    def recalculate_lab(self, lab_id, dry_run):
        """Recalculate averages for a specific lab"""
        try:
            lab = Lab.objects.get(id=lab_id)
            self.stdout.write(f'Recalculating averages for lab: {lab.name}')

            if not dry_run:
                LabCategoryAverage.update_lab_averages(lab_id)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated averages for lab {lab_id}')
                )
            else:
                # Show what would be updated
                categories = RatingCategory.objects.filter(is_active=True)
                self.stdout.write(f'Would update {categories.count()} categories for lab {lab_id}')

        except Lab.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Lab with ID {lab_id} does not exist')
            )

    def recalculate_category(self, category_id, dry_run):
        """Recalculate a specific category for all labs"""
        try:
            category = RatingCategory.objects.get(id=category_id)
            labs_count = Lab.objects.count()

            self.stdout.write(
                f'Recalculating "{category.display_name}" for {labs_count} labs'
            )

            if not dry_run:
                LabCategoryAverage.update_category_for_all_labs(category_id)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated {category.display_name} for all labs')
                )
            else:
                self.stdout.write(f'Would update {labs_count} labs for category {category_id}')

        except RatingCategory.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Category with ID {category_id} does not exist')
            )

    def recalculate_all(self, dry_run, batch_size):
        """Recalculate all averages for all labs"""
        labs = Lab.objects.all()
        total_labs = labs.count()
        categories_count = RatingCategory.objects.filter(is_active=True).count()

        self.stdout.write(
            f'Recalculating averages for {total_labs} labs and {categories_count} categories'
        )

        if dry_run:
            self.stdout.write(
                f'DRY RUN: Would process {total_labs} labs in batches of {batch_size}'
            )
            return

        processed = 0
        failed = 0

        # Process labs in batches for better performance
        for i in range(0, total_labs, batch_size):
            batch_labs = labs[i:i + batch_size]

            with transaction.atomic():
                for lab in batch_labs:
                    try:
                        LabCategoryAverage.update_lab_averages(lab.id)
                        processed += 1

                        if processed % 10 == 0:  # Progress update every 10 labs
                            progress = (processed / total_labs) * 100
                            self.stdout.write(f'Progress: {processed}/{total_labs} ({progress:.1f}%)')

                    except Exception as e:
                        failed += 1
                        self.stdout.write(
                            self.style.WARNING(f'Failed to update lab {lab.id}: {str(e)}')
                        )

        self.stdout.write(
            self.style.SUCCESS(f'✓ Processed {processed} labs successfully')
        )

        if failed > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠ Failed to process {failed} labs')
            )

        # Show final statistics
        self.show_statistics()

    def show_statistics(self):
        """Show statistics about precomputed averages"""
        total_averages = LabCategoryAverage.objects.count()
        labs_with_averages = LabCategoryAverage.objects.values('lab').distinct().count()
        categories_tracked = LabCategoryAverage.objects.values('category').distinct().count()

        self.stdout.write('\n' + '='*50)
        self.stdout.write('STATISTICS:')
        self.stdout.write(f'Total precomputed averages: {total_averages}')
        self.stdout.write(f'Labs with averages: {labs_with_averages}')
        self.stdout.write(f'Categories tracked: {categories_tracked}')
        self.stdout.write('='*50)