# Migration to rename mock_interview_sessions to interview_sessions

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE mock_interview_sessions RENAME TO interview_sessions;",
            reverse_sql="ALTER TABLE interview_sessions RENAME TO mock_interview_sessions;",
        ),
    ]