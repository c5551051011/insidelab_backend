# Migration to rename mock_interview_sessions to interview_sessions
# This is now a no-op since 0003_initial creates the table directly with correct name

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0001_initial'),
    ]

    operations = [
        # No-op: The table will be created with the correct name in 0003_initial
    ]