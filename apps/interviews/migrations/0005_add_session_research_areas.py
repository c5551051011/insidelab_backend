# Migration to add SessionResearchArea model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0004_add_research_area_field'),
        ('publications', '0007_populate_research_areas_by_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionResearchArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=1, help_text='Priority order (1 = highest)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('research_area', models.ForeignKey(help_text='Research area for matching', on_delete=django.db.models.deletion.CASCADE, to='publications.researcharea')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='research_areas', to='interviews.mockinterviewsession')),
            ],
            options={
                'db_table': 'session_research_areas',
                'ordering': ['priority'],
                'unique_together': {('session', 'research_area')},
            },
        ),
    ]