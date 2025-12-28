# Migration to add department field to ResearchArea model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0007_merge_20251030_1034'),
        ('publications', '0005_populate_venue_tiers'),
    ]

    operations = [
        # Add department field to ResearchArea
        migrations.AddField(
            model_name='researcharea',
            name='department',
            field=models.ForeignKey(
                blank=True,
                help_text='Department this research area belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='research_areas',
                to='universities.department'
            ),
        ),

        # Remove the old unique constraint on name alone - handled by AlterUniqueTogether

        # Add new unique constraint on name and department
        migrations.AlterUniqueTogether(
            name='researcharea',
            unique_together={('name', 'department')},
        ),

        # Update ordering
        migrations.AlterModelOptions(
            name='researcharea',
            options={'ordering': ['department__name', 'name']},
        ),
    ]