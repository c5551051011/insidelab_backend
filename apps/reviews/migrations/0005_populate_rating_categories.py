# Generated migration to populate initial rating categories

from django.db import migrations


def create_initial_categories(apps, schema_editor):
    RatingCategory = apps.get_model('reviews', 'RatingCategory')

    categories = [
        {
            'name': 'mentorship_quality',
            'display_name': 'Mentorship Quality',
            'description': 'Quality of mentorship and guidance provided',
            'sort_order': 1
        },
        {
            'name': 'research_environment',
            'display_name': 'Research Environment',
            'description': 'Quality of research facilities and environment',
            'sort_order': 2
        },
        {
            'name': 'work_life_balance',
            'display_name': 'Work-Life Balance',
            'description': 'Balance between work demands and personal life',
            'sort_order': 3
        },
        {
            'name': 'career_support',
            'display_name': 'Career Support',
            'description': 'Support for career development and opportunities',
            'sort_order': 4
        },
        {
            'name': 'funding_resources',
            'display_name': 'Funding & Resources',
            'description': 'Availability of funding and research resources',
            'sort_order': 5
        },
        {
            'name': 'collaboration_culture',
            'display_name': 'Collaboration Culture',
            'description': 'Culture of collaboration and teamwork',
            'sort_order': 6
        },
    ]

    for category_data in categories:
        RatingCategory.objects.create(**category_data)


def reverse_categories(apps, schema_editor):
    RatingCategory = apps.get_model('reviews', 'RatingCategory')
    RatingCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_ratingcategory_remove_review_career_support_rating_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, reverse_categories),
    ]