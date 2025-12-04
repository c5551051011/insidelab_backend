from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_merge_20251030_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='department',
        ),
    ]
