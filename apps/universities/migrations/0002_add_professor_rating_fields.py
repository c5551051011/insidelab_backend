# Generated migration for Professor rating cache fields

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='professor',
            name='overall_rating',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Cached average rating from reviews',
                max_digits=3,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(5)
                ]
            ),
        ),
        migrations.AddField(
            model_name='professor',
            name='review_count',
            field=models.IntegerField(
                default=0,
                help_text='Cached count of active reviews'
            ),
        ),
    ]