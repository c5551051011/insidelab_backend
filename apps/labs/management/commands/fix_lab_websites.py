"""
Management command to fix specific lab website mappings with more accurate URLs.
"""

from django.core.management.base import BaseCommand
from apps.labs.models import Lab

class Command(BaseCommand):
    help = 'Fix specific lab website mappings with more accurate URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        # More accurate lab website mappings
        accurate_mappings = {
            # Stanford Labs - Fix mappings
            "Stanford Natural Language Processing Group": "https://nlp.stanford.edu/",
            "Stanford Artificial Intelligence Laboratory (SAIL)": "http://ai.stanford.edu/",
            "Stanford Vision and Learning Lab (SVL)": "http://svl.stanford.edu/",
            "Stanford Robotics Laboratory": "http://robotics.stanford.edu/",

            # MIT Labs - More specific URLs
            "Learning and Intelligent Systems Group": "http://lis.csail.mit.edu/",
            "Machine Learning Theory Group": "http://people.csail.mit.edu/moitra/",
            "Machine Learning Group": "http://www.csail.mit.edu/research/artificial-intelligence",
            "Distributed Robotics Laboratory": "http://danielarus.csail.mit.edu/",
            "Intelligent Interactive Systems Group": "http://interactive.mit.edu/",

            # Carnegie Mellon Labs
            "Human-Computer Interaction Institute (HCII)": "https://hcii.cmu.edu/",
            "Machine Learning Department": "http://www.ml.cmu.edu/",
            "Language Technologies Institute (LTI)": "https://www.lti.cs.cmu.edu/",
            "CyLab Security & Privacy Institute": "https://www.cylab.cmu.edu/",

            # UC Berkeley Labs
            "Berkeley Artificial Intelligence Research (BAIR) Lab": "https://bair.berkeley.edu/",
            "Computer Security Group": "http://security.cs.berkeley.edu/",
            "Cryptography and Information Security Group": "http://security.cs.berkeley.edu/",

            # Princeton Labs
            "Princeton Graphics Group": "http://gfx.cs.princeton.edu/",
            "Princeton Privacy and Security Lab": "http://security.cs.princeton.edu/",
            "Princeton NLP Group": "http://nlp.cs.princeton.edu/",
            "Princeton Visual AI Lab": "http://vision.cs.princeton.edu/",
            "Princeton Computational Imaging Lab": "http://light.princeton.edu/",
            "Computer Vision Group": "http://vision.cs.princeton.edu/",

            # Cornell Labs
            "Cornell Graphics and Vision Group": "http://www.graphics.cornell.edu/",
            "Cornell Theory Group": "http://www.cs.cornell.edu/theory/",
            "Initiative for CryptoCurrencies and Contracts (IC3)": "https://www.initc3.org/",

            # Harvard Labs
            "Architecture, Circuits and Compilers Group": "http://www.eecs.harvard.edu/~htk/",
            "Harvard Biodesign Lab": "http://biodesign.seas.harvard.edu/",
            "Harvard Microrobotics Laboratory": "http://micro.seas.harvard.edu/",
            "Data to Actionable Knowledge (DtAK) Lab": "http://dtak.seas.harvard.edu/",

            # Robotics specific fixes
            "Robotics Institute": "https://www.ri.cmu.edu/",  # This should be CMU, not Stanford
            "Robotics and Intelligent Machines Lab (AUTOLAB)": "https://autolab.berkeley.edu/",  # UC Berkeley
            "EmPRISE Lab (Empowering People through Robotics, Intelligent Systems, and Embodied AI)": "https://emprise.cs.cornell.edu/",  # Cornell
            "Interactive Robotics Group": "http://interactive-robotics.seas.harvard.edu/",  # Harvard

            # Graphics and Systems fixes
            "Computer Graphics Group": "http://graphics.seas.harvard.edu/",  # This should be Harvard
            "Systems Research Group": "http://systems.seas.harvard.edu/",  # Harvard

            # Security labs fixes
            "Applied Cryptography Group": "http://crypto.stanford.edu/",  # Stanford crypto
        }

        updated_count = 0

        for lab_name, correct_url in accurate_mappings.items():
            try:
                lab = Lab.objects.get(name=lab_name)
                if options['dry_run']:
                    self.stdout.write(f"Would fix {lab.name}: {lab.website} -> {correct_url}")
                else:
                    old_url = lab.website
                    lab.website = correct_url
                    lab.save()
                    self.stdout.write(f"Fixed {lab.name}: {old_url} -> {correct_url}")
                updated_count += 1
            except Lab.DoesNotExist:
                self.stdout.write(f"Lab not found: {lab_name}")

        if options['dry_run']:
            self.stdout.write(f"DRY RUN: Would fix {updated_count} lab websites")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully fixed {updated_count} lab websites")
            )