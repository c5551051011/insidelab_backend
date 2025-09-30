# apps/universities/management/commands/populate_university_domains.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.universities.models import University, UniversityEmailDomain


class Command(BaseCommand):
    help = 'Populate university email domains for verification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing domains',
        )

    def handle(self, *args, **options):
        force = options['force']

        # Korean Universities and their email domains
        university_domains = {
            # SKY Universities
            'Seoul National University': [
                'snu.ac.kr',
                'student.snu.ac.kr',
                'alumni.snu.ac.kr'
            ],
            'Yonsei University': [
                'yonsei.ac.kr',
                'student.yonsei.ac.kr',
                'alumni.yonsei.ac.kr'
            ],
            'Korea University': [
                'korea.ac.kr',
                'student.korea.ac.kr',
                'alumni.korea.ac.kr'
            ],

            # KAIST and POSTECH
            'Korea Advanced Institute of Science and Technology': [
                'kaist.ac.kr',
                'student.kaist.ac.kr'
            ],
            'Pohang University of Science and Technology': [
                'postech.ac.kr',
                'student.postech.ac.kr'
            ],

            # Other Major Universities
            'Hanyang University': [
                'hanyang.ac.kr',
                'student.hanyang.ac.kr'
            ],
            'Sungkyunkwan University': [
                'skku.edu',
                'student.skku.edu'
            ],
            'Kyung Hee University': [
                'khu.ac.kr',
                'student.khu.ac.kr'
            ],
            'Sogang University': [
                'sogang.ac.kr',
                'student.sogang.ac.kr'
            ],
            'Ewha Womans University': [
                'ewha.ac.kr',
                'student.ewha.ac.kr'
            ],
            'Konkuk University': [
                'konkuk.ac.kr',
                'student.konkuk.ac.kr'
            ],
            'Inha University': [
                'inha.ac.kr',
                'student.inha.ac.kr'
            ],
            'Chung-Ang University': [
                'cau.ac.kr',
                'student.cau.ac.kr'
            ],
            'Dongguk University': [
                'dongguk.edu',
                'student.dongguk.edu'
            ],
            'Hongik University': [
                'hongik.ac.kr',
                'student.hongik.ac.kr'
            ],

            # US Top Universities (Ivy League + Top Tech Schools)
            'Massachusetts Institute of Technology': [
                'mit.edu',
                'student.mit.edu'
            ],
            'Stanford University': [
                'stanford.edu',
                'student.stanford.edu'
            ],
            'Harvard University': [
                'harvard.edu',
                'student.harvard.edu'
            ],
            'California Institute of Technology': [
                'caltech.edu',
                'student.caltech.edu'
            ],
            'University of California, Berkeley': [
                'berkeley.edu',
                'student.berkeley.edu'
            ],
            'Carnegie Mellon University': [
                'cmu.edu',
                'student.cmu.edu'
            ],
            'Princeton University': [
                'princeton.edu',
                'student.princeton.edu'
            ],
            'Yale University': [
                'yale.edu',
                'student.yale.edu'
            ],
            'Columbia University': [
                'columbia.edu',
                'student.columbia.edu'
            ],
            'University of Pennsylvania': [
                'upenn.edu',
                'student.upenn.edu'
            ],
            'Cornell University': [
                'cornell.edu',
                'student.cornell.edu'
            ],
            'Dartmouth College': [
                'dartmouth.edu',
                'student.dartmouth.edu'
            ],
            'Brown University': [
                'brown.edu',
                'student.brown.edu'
            ],
            'University of Chicago': [
                'uchicago.edu',
                'student.uchicago.edu'
            ],
            'Northwestern University': [
                'northwestern.edu',
                'student.northwestern.edu'
            ],
            'Johns Hopkins University': [
                'jhu.edu',
                'student.jhu.edu'
            ],
            'Duke University': [
                'duke.edu',
                'student.duke.edu'
            ],
            'Vanderbilt University': [
                'vanderbilt.edu',
                'student.vanderbilt.edu'
            ],
            'Rice University': [
                'rice.edu',
                'student.rice.edu'
            ],
            'Georgia Institute of Technology': [
                'gatech.edu',
                'student.gatech.edu'
            ],
            'University of California, Los Angeles': [
                'ucla.edu',
                'student.ucla.edu'
            ],
            'University of California, San Diego': [
                'ucsd.edu',
                'student.ucsd.edu'
            ],
            'University of Michigan': [
                'umich.edu',
                'student.umich.edu'
            ],
            'University of Illinois at Urbana-Champaign': [
                'illinois.edu',
                'student.illinois.edu'
            ],
            'University of Washington': [
                'uw.edu',
                'student.uw.edu'
            ],
            'New York University': [
                'nyu.edu',
                'student.nyu.edu'
            ],
            'University of Southern California': [
                'usc.edu',
                'student.usc.edu'
            ],
            'Boston University': [
                'bu.edu',
                'student.bu.edu'
            ],
            'University of Texas at Austin': [
                'utexas.edu',
                'student.utexas.edu'
            ],
            'Pennsylvania State University': [
                'psu.edu',
                'student.psu.edu'
            ],
            'Purdue University': [
                'purdue.edu',
                'student.purdue.edu'
            ],
            'Virginia Tech': [
                'vt.edu',
                'student.vt.edu'
            ],

            # International Universities (Popular for Korean students)
            'University of Toronto': [
                'utoronto.ca',
                'mail.utoronto.ca'
            ],
            'University of Cambridge': [
                'cam.ac.uk',
                'student.cam.ac.uk'
            ],
            'University of Oxford': [
                'ox.ac.uk',
                'student.ox.ac.uk'
            ],
            'ETH Zurich': [
                'ethz.ch',
                'student.ethz.ch'
            ],
            'National University of Singapore': [
                'nus.edu.sg',
                'student.nus.edu.sg'
            ],
        }

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for university_name, domains in university_domains.items():
                # Determine country and location
                if any(d.endswith('.ac.kr') for d in domains):
                    country = 'South Korea'
                    state = 'Seoul' if 'Seoul' in university_name else ''
                    city = 'Seoul' if 'Seoul' in university_name else ''
                elif any(d.endswith('.edu') for d in domains):
                    country = 'United States'
                    # Set states for US universities
                    if 'MIT' in university_name or 'Harvard' in university_name or 'Boston' in university_name:
                        state, city = 'Massachusetts', 'Boston'
                    elif 'Stanford' in university_name or 'Berkeley' in university_name or 'UCLA' in university_name or 'USC' in university_name or 'Caltech' in university_name:
                        state, city = 'California', 'Los Angeles' if 'UCLA' in university_name else 'San Francisco'
                    elif 'Princeton' in university_name:
                        state, city = 'New Jersey', 'Princeton'
                    elif 'Yale' in university_name:
                        state, city = 'Connecticut', 'New Haven'
                    elif 'Columbia' in university_name or 'NYU' in university_name:
                        state, city = 'New York', 'New York City'
                    elif 'Cornell' in university_name:
                        state, city = 'New York', 'Ithaca'
                    elif 'Carnegie Mellon' in university_name:
                        state, city = 'Pennsylvania', 'Pittsburgh'
                    else:
                        state, city = '', ''
                elif any(d.endswith('.ca') for d in domains):
                    country, state, city = 'Canada', 'Ontario', 'Toronto'
                elif any(d.endswith('.ac.uk') for d in domains):
                    country, state, city = 'United Kingdom', '', 'Cambridge' if 'Cambridge' in university_name else 'Oxford'
                elif any(d.endswith('.ch') for d in domains):
                    country, state, city = 'Switzerland', '', 'Zurich'
                elif any(d.endswith('.edu.sg') for d in domains):
                    country, state, city = 'Singapore', '', 'Singapore'
                else:
                    country, state, city = 'Unknown', '', ''

                # Get or create university
                university, created = University.objects.get_or_create(
                    name=university_name,
                    defaults={
                        'country': country,
                        'state': state,
                        'city': city,
                    }
                )

                if created:
                    self.stdout.write(f'Created university: {university_name}')

                # Add email domains
                for domain in domains:
                    domain_obj, domain_created = UniversityEmailDomain.objects.get_or_create(
                        domain=domain,
                        defaults={
                            'university': university,
                            'is_verified': True,  # Pre-verified major universities
                            'verification_type': 'student' if 'student' in domain else 'official'
                        }
                    )

                    if domain_created:
                        created_count += 1
                        self.stdout.write(f'  Added domain: {domain}')
                    elif force:
                        domain_obj.university = university
                        domain_obj.is_verified = True
                        domain_obj.save()
                        updated_count += 1
                        self.stdout.write(f'  Updated domain: {domain}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {created_count} new domains and updated {updated_count} existing domains'
            )
        )

        # Display statistics
        total_universities = University.objects.count()
        total_domains = UniversityEmailDomain.objects.count()
        verified_domains = UniversityEmailDomain.objects.filter(is_verified=True).count()

        self.stdout.write(f'\nStatistics:')
        self.stdout.write(f'Total Universities: {total_universities}')
        self.stdout.write(f'Total Email Domains: {total_domains}')
        self.stdout.write(f'Verified Domains: {verified_domains}')