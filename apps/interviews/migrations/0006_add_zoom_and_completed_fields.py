# Migration to add zoom_link and completed_at fields to MockInterviewSession

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0005_add_session_research_areas'),
    ]

    operations = [
        migrations.AddField(
            model_name='mockinterviewsession',
            name='zoom_link',
            field=models.URLField(blank=True, help_text='Zoom meeting link for confirmed sessions'),
        ),
        migrations.AddField(
            model_name='mockinterviewsession',
            name='completed_at',
            field=models.DateTimeField(blank=True, help_text='Timestamp when session was completed', null=True),
        ),
    ]