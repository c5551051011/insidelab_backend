# Migration to add ResearchArea model and research_area field to MockInterviewSession

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0002_rename_table_to_interview_sessions'),
    ]

    operations = [
        # Create ResearchArea model
        migrations.CreateModel(
            name='ResearchArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'interview_research_areas',
                'ordering': ['name'],
            },
        ),

        # Add research_area field to MockInterviewSession
        migrations.AddField(
            model_name='mockinterviewsession',
            name='research_area',
            field=models.ForeignKey(
                blank=True,
                help_text='Primary research area for interviewer matching',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='interviews.researcharea'
            ),
        ),
    ]