# Generated migration to change RecruitmentStatus from lab to professor

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0001_initial'),
        ('labs', '0008_remove_lab_professor'),
    ]

    operations = [
        # Remove the old lab field
        migrations.RemoveField(
            model_name='recruitmentstatus',
            name='lab',
        ),
        # Add the new professor field
        migrations.AddField(
            model_name='recruitmentstatus',
            name='professor',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recruitment_status',
                to='universities.professor'
            ),
        ),
    ]