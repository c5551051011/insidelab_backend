# Generated migration for UserResearchProfile model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserResearchProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_research_area', models.CharField(blank=True, help_text='Main research area (e.g., Machine Learning, Computer Vision)', max_length=200)),
                ('specialties_interests', models.JSONField(default=list, help_text='List of specific specialties and interests')),
                ('research_keywords', models.JSONField(default=list, help_text='Keywords related to research interests')),
                ('academic_background', models.TextField(blank=True, help_text='Brief academic background or experience')),
                ('research_goals', models.TextField(blank=True, help_text='Research goals or career objectives')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='research_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_research_profiles',
            },
        ),
    ]