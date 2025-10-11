#!/usr/bin/env python
"""
Script to populate all academic venues based on comprehensive classification.
This script ensures all venues from the academic ranking are in the database.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insidelab.settings')
django.setup()

from apps.publications.models import Venue


def create_venue_if_not_exists(name, short_name, type_choice, tier, field='', description=''):
    """Create venue if it doesn't exist"""
    venue, created = Venue.objects.get_or_create(
        name=name,
        type=type_choice,
        defaults={
            'short_name': short_name,
            'tier': tier,
            'field': field,
            'description': description
        }
    )
    if created:
        print(f"Created: {name} ({short_name}) - {tier}")
    else:
        # Update tier if it exists but tier is different
        if venue.tier != tier:
            venue.tier = tier
            venue.save()
            print(f"Updated tier for: {name} - {tier}")
    return venue


def populate_top_tier_venues():
    """Top-tier (S급) venues"""
    print("=== Creating Top-tier (S급) Venues ===")

    # Machine Learning & AI
    venues = [
        ("Neural Information Processing Systems", "NeurIPS", "conference", "Machine Learning"),
        ("Advances in Neural Information Processing Systems", "NeurIPS", "conference", "Machine Learning"),
        ("International Conference on Machine Learning", "ICML", "conference", "Machine Learning"),
        ("International Conference on Learning Representations", "ICLR", "conference", "Machine Learning"),
        ("AAAI Conference on Artificial Intelligence", "AAAI", "conference", "Artificial Intelligence"),
        ("International Joint Conference on Artificial Intelligence", "IJCAI", "conference", "Artificial Intelligence"),

        # Computer Vision
        ("IEEE/CVF Conference on Computer Vision and Pattern Recognition", "CVPR", "conference", "Computer Vision"),
        ("Computer Vision and Pattern Recognition", "CVPR", "conference", "Computer Vision"),
        ("International Conference on Computer Vision", "ICCV", "conference", "Computer Vision"),
        ("European Conference on Computer Vision", "ECCV", "conference", "Computer Vision"),

        # Natural Language Processing
        ("Annual Meeting of the Association for Computational Linguistics", "ACL", "conference", "Natural Language Processing"),
        ("Association for Computational Linguistics", "ACL", "conference", "Natural Language Processing"),
        ("Empirical Methods in Natural Language Processing", "EMNLP", "conference", "Natural Language Processing"),
        ("North American Chapter of the Association for Computational Linguistics", "NAACL", "conference", "Natural Language Processing"),

        # Systems & Architecture
        ("USENIX Symposium on Operating Systems Design and Implementation", "OSDI", "conference", "Systems"),
        ("ACM Symposium on Operating Systems Principles", "SOSP", "conference", "Systems"),
        ("International Symposium on Computer Architecture", "ISCA", "conference", "Computer Architecture"),
        ("IEEE/ACM International Symposium on Microarchitecture", "MICRO", "conference", "Computer Architecture"),

        # Networking & Security
        ("ACM SIGCOMM Conference", "SIGCOMM", "conference", "Networking"),
        ("USENIX Symposium on Networked Systems Design and Implementation", "NSDI", "conference", "Networking"),
        ("Network and Distributed System Security Symposium", "NDSS", "conference", "Security"),
        ("ACM Conference on Computer and Communications Security", "CCS", "conference", "Security"),
        ("USENIX Security Symposium", "USENIX Security", "conference", "Security"),
        ("IEEE Symposium on Security and Privacy", "IEEE S&P", "conference", "Security"),

        # Software Engineering
        ("International Conference on Software Engineering", "ICSE", "conference", "Software Engineering"),
        ("ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering", "FSE", "conference", "Software Engineering"),
        ("ACM SIGPLAN Conference on Programming Language Design and Implementation", "PLDI", "conference", "Programming Languages"),

        # Database & Data Mining
        ("ACM SIGMOD International Conference on Management of Data", "SIGMOD", "conference", "Database"),
        ("International Conference on Very Large Data Bases", "VLDB", "conference", "Database"),
        ("ACM SIGKDD International Conference on Knowledge Discovery and Data Mining", "KDD", "conference", "Data Mining"),
        ("IEEE International Conference on Data Engineering", "ICDE", "conference", "Database"),

        # Human-Computer Interaction
        ("ACM CHI Conference on Human Factors in Computing Systems", "CHI", "conference", "Human-Computer Interaction"),
        ("ACM Symposium on User Interface Software and Technology", "UIST", "conference", "Human-Computer Interaction"),

        # Theory
        ("ACM Symposium on Theory of Computing", "STOC", "conference", "Theoretical Computer Science"),
        ("IEEE Symposium on Foundations of Computer Science", "FOCS", "conference", "Theoretical Computer Science"),

        # Electrical Engineering
        ("IEEE International Solid-State Circuits Conference", "ISSCC", "conference", "Electronics"),
        ("Design Automation Conference", "DAC", "conference", "Electronics"),
        ("IEEE/ACM International Conference on Computer-Aided Design", "ICCAD", "conference", "Electronics"),
        ("IEEE International Conference on Acoustics, Speech and Signal Processing", "ICASSP", "conference", "Signal Processing"),
        ("IEEE Applied Power Electronics Conference and Exposition", "APEC", "conference", "Power Electronics"),
        ("IEEE Energy Conversion Congress and Exposition", "ECCE", "conference", "Power Electronics"),
        ("IEEE International Conference on Communications", "ICC", "conference", "Communications"),
        ("IEEE Global Communications Conference", "GLOBECOM", "conference", "Communications"),
    ]

    for name, short_name, type_choice, field in venues:
        create_venue_if_not_exists(name, short_name, type_choice, 'top', field)


def populate_high_tier_venues():
    """High-tier (A급) venues"""
    print("\n=== Creating High-tier (A급) Venues ===")

    venues = [
        # Machine Learning & AI
        ("International Conference on Artificial Intelligence and Statistics", "AISTATS", "conference", "Machine Learning"),
        ("Conference on Uncertainty in Artificial Intelligence", "UAI", "conference", "Machine Learning"),
        ("Conference on Robot Learning", "CoRL", "conference", "Machine Learning"),
        ("Conference on Learning Theory", "COLT", "conference", "Machine Learning"),

        # Computer Vision
        ("British Machine Vision Conference", "BMVC", "conference", "Computer Vision"),
        ("IEEE/CVF Winter Conference on Applications of Computer Vision", "WACV", "conference", "Computer Vision"),
        ("International Conference on 3D Vision", "3DV", "conference", "Computer Vision"),

        # Natural Language Processing
        ("Conference on Computational Natural Language Learning", "CoNLL", "conference", "Natural Language Processing"),
        ("European Chapter of the Association for Computational Linguistics", "EACL", "conference", "Natural Language Processing"),
        ("International Conference on Computational Linguistics", "COLING", "conference", "Natural Language Processing"),

        # Robotics
        ("IEEE International Conference on Robotics and Automation", "ICRA", "conference", "Robotics"),
        ("IEEE/RSJ International Conference on Intelligent Robots and Systems", "IROS", "conference", "Robotics"),
        ("Robotics: Science and Systems", "RSS", "conference", "Robotics"),

        # Systems & Architecture
        ("International Conference on Architectural Support for Programming Languages and Operating Systems", "ASPLOS", "conference", "Systems"),
        ("European Conference on Computer Systems", "EuroSys", "conference", "Systems"),
        ("IEEE International Symposium on High Performance Computer Architecture", "HPCA", "conference", "Computer Architecture"),
        ("USENIX Annual Technical Conference", "ATC", "conference", "Systems"),

        # Networking & Security
        ("IEEE Conference on Computer Communications", "INFOCOM", "conference", "Networking"),
        ("ACM Internet Measurement Conference", "IMC", "conference", "Networking"),
        ("International Cryptology Conference", "CRYPTO", "conference", "Cryptography"),
        ("International Conference on the Theory and Applications of Cryptographic Techniques", "EUROCRYPT", "conference", "Cryptography"),

        # Software Engineering
        ("IEEE/ACM International Conference on Automated Software Engineering", "ASE", "conference", "Software Engineering"),
        ("ACM SIGSOFT International Symposium on Software Testing and Analysis", "ISSTA", "conference", "Software Engineering"),
        ("ACM SIGPLAN International Conference on Object-Oriented Programming, Systems, Languages, and Applications", "OOPSLA", "conference", "Programming Languages"),

        # Database & Data Mining
        ("IEEE International Conference on Data Mining", "ICDM", "conference", "Data Mining"),
        ("SIAM International Conference on Data Mining", "SDM", "conference", "Data Mining"),
        ("ACM International Conference on Web Search and Data Mining", "WSDM", "conference", "Data Mining"),

        # Graphics & Multimedia
        ("ACM SIGGRAPH Conference on Computer Graphics and Interactive Techniques", "SIGGRAPH", "conference", "Computer Graphics"),
        ("ACM SIGGRAPH Asia Conference on Computer Graphics and Interactive Techniques", "SIGGRAPH Asia", "conference", "Computer Graphics"),
        ("ACM International Conference on Multimedia", "ACM MM", "conference", "Multimedia"),

        # HCI
        ("ACM Conference on Computer-Supported Cooperative Work and Social Computing", "CSCW", "conference", "Human-Computer Interaction"),
        ("ACM International Conference on Intelligent User Interfaces", "IUI", "conference", "Human-Computer Interaction"),

        # Electrical Engineering
        ("IEEE International Symposium on Circuits and Systems", "ISCAS", "conference", "Electronics"),
        ("Symposium on VLSI Circuits", "VLSI Circuits", "conference", "Electronics"),
        ("ACM SIGBED International Conference on Embedded Software", "EMSOFT", "conference", "Embedded Systems"),
        ("IEEE Real-Time and Embedded Technology and Applications Symposium", "RTAS", "conference", "Embedded Systems"),
        ("Design, Automation & Test in Europe Conference & Exhibition", "DATE", "conference", "Electronics"),
        ("European Signal Processing Conference", "EUSIPCO", "conference", "Signal Processing"),
        ("IEEE Wireless Communications and Networking Conference", "WCNC", "conference", "Communications"),
        ("IEEE Vehicular Technology Conference", "VTC", "conference", "Communications"),

        # Industrial & Systems Engineering
        ("Winter Simulation Conference", "WSC", "conference", "Industrial Engineering"),
        ("IEEE International Conference on Automation Science and Engineering", "CASE", "conference", "Industrial Engineering"),
        ("IEEE International Conference on Emerging Technologies and Factory Automation", "ETFA", "conference", "Industrial Engineering"),
        ("Human Factors and Ergonomics Society Annual Meeting", "HFES", "conference", "Human Factors"),
    ]

    for name, short_name, type_choice, field in venues:
        create_venue_if_not_exists(name, short_name, type_choice, 'high', field)


def populate_mid_tier_venues():
    """Mid-tier (B급) venues"""
    print("\n=== Creating Mid-tier (B급) Venues ===")

    venues = [
        # Machine Learning & AI
        ("European Conference on Artificial Intelligence", "ECAI", "conference", "Artificial Intelligence"),
        ("Pacific Rim International Conference on Artificial Intelligence", "PRICAI", "conference", "Artificial Intelligence"),
        ("International Conference on Artificial Neural Networks", "ICANN", "conference", "Machine Learning"),

        # Computer Vision
        ("Asian Conference on Computer Vision", "ACCV", "conference", "Computer Vision"),
        ("IEEE International Conference on Image Processing", "ICIP", "conference", "Computer Vision"),
        ("International Conference on Pattern Recognition", "ICPR", "conference", "Computer Vision"),

        # Robotics
        ("IEEE-RAS International Conference on Humanoid Robots", "Humanoids", "conference", "Robotics"),
        ("International Conference on Control, Automation, Robotics and Vision", "ICARCV", "conference", "Robotics"),

        # Systems
        ("ACM/IFIP/USENIX International Conference on Distributed Systems Platforms and Open Distributed Processing", "Middleware", "conference", "Systems"),
        ("IEEE International Conference on Distributed Computing Systems", "ICDCS", "conference", "Systems"),
        ("IEEE International Conference on Cluster Computing", "CLUSTER", "conference", "Systems"),

        # Networking
        ("IEEE International Conference on Network Protocols", "ICNP", "conference", "Networking"),
        ("ACM International Conference on Emerging Networking Experiments and Technologies", "CoNEXT", "conference", "Networking"),

        # Software Engineering
        ("IEEE International Conference on Software Maintenance and Evolution", "ICSME", "conference", "Software Engineering"),
        ("IEEE/ACM International Conference on Program Comprehension", "ICPC", "conference", "Software Engineering"),
        ("IEEE/ACM International Conference on Mining Software Repositories", "MSR", "conference", "Software Engineering"),

        # Web & IR
        ("The Web Conference", "WWW", "conference", "Web Technologies"),
        ("ACM SIGIR Conference on Research and Development in Information Retrieval", "SIGIR", "conference", "Information Retrieval"),
        ("ACM International Conference on Information and Knowledge Management", "CIKM", "conference", "Information Management"),

        # Electrical Engineering
        ("IEEE International Midwest Symposium on Circuits and Systems", "MWSCAS", "conference", "Electronics"),
        ("American Control Conference", "ACC", "conference", "Control Systems"),
        ("IEEE Conference on Decision and Control", "CDC", "conference", "Control Systems"),

        # Industrial Engineering
        ("IIE Annual Conference", "IIE Annual", "conference", "Industrial Engineering"),
        ("Institute of Industrial and Systems Engineers Annual Conference", "IISE", "conference", "Industrial Engineering"),
        ("International Conference on Flexible Automation and Intelligent Manufacturing", "FAIM", "conference", "Manufacturing"),
        ("CIRP Conference", "CIRP", "conference", "Manufacturing"),
    ]

    for name, short_name, type_choice, field in venues:
        create_venue_if_not_exists(name, short_name, type_choice, 'mid', field)


def populate_journal_venues():
    """Add important journals"""
    print("\n=== Creating Important Journals ===")

    journals = [
        # Top-tier journals
        ("Nature Machine Intelligence", "Nature MI", "journal", "top", "Machine Learning"),
        ("Journal of Machine Learning Research", "JMLR", "journal", "top", "Machine Learning"),
        ("IEEE Transactions on Pattern Analysis and Machine Intelligence", "TPAMI", "journal", "top", "Computer Vision"),
        ("Transactions of the Association for Computational Linguistics", "TACL", "journal", "top", "Natural Language Processing"),
        ("ACM Transactions on Computer Systems", "TOCS", "journal", "top", "Systems"),
        ("IEEE Journal on Selected Areas in Communications", "JSAC", "journal", "top", "Communications"),
        ("IEEE Journal of Solid-State Circuits", "JSSC", "journal", "top", "Electronics"),
        ("IEEE Transactions on Signal Processing", "TSP", "journal", "top", "Signal Processing"),
        ("IEEE Transactions on Robotics", "T-RO", "journal", "top", "Robotics"),

        # High-tier journals
        ("Operations Research", "OR", "journal", "high", "Operations Research"),
        ("Management Science", "MS", "journal", "high", "Management Science"),
        ("Manufacturing & Service Operations Management", "MSOM", "journal", "high", "Operations Management"),
        ("IIE Transactions", "IIE Trans", "journal", "high", "Industrial Engineering"),
    ]

    for name, short_name, type_choice, tier, field in journals:
        create_venue_if_not_exists(name, short_name, type_choice, tier, field)


def main():
    """Main function to populate all venues"""
    print("Starting venue population...")

    populate_top_tier_venues()
    populate_high_tier_venues()
    populate_mid_tier_venues()
    populate_journal_venues()

    # Set all workshop-type venues to workshop tier
    workshop_venues = Venue.objects.filter(type='workshop')
    updated_count = workshop_venues.update(tier='workshop')
    if updated_count > 0:
        print(f"\n=== Updated {updated_count} workshop venues to 'workshop' tier ===")

    print(f"\n=== Venue Population Complete ===")
    print(f"Total venues in database: {Venue.objects.count()}")
    print("\nVenue count by tier:")
    for tier, display in Venue.TIER_CHOICES:
        count = Venue.objects.filter(tier=tier).count()
        print(f"  {display}: {count}")


if __name__ == '__main__':
    main()