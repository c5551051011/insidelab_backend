from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0007_merge_20251030_1034'),
        ('labs', '0008_remove_lab_professor'),
        ('publications', '0008_alter_researcharea_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicationProfessor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('pi', 'Principal Investigator'), ('co_pi', 'Co-Principal Investigator'), ('corresponding', 'Corresponding Author'), ('first', 'First Author'), ('last', 'Last Author'), ('author', 'Author')], default='author', max_length=20)),
                ('author_order', models.PositiveIntegerField(blank=True, null=True)),
                ('affiliation', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('affiliation_lab', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='labs.lab')),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='universities.professor')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publications.publication')),
            ],
            options={
                'db_table': 'publication_professors',
            },
        ),
        migrations.AddField(
            model_name='publication',
            name='professors',
            field=models.ManyToManyField(blank=True, related_name='publications', through='publications.PublicationProfessor', to='universities.professor'),
        ),
        migrations.AddIndex(
            model_name='publicationprofessor',
            index=models.Index(fields=['professor'], name='publications_professor_idx'),
        ),
        migrations.AddIndex(
            model_name='publicationprofessor',
            index=models.Index(fields=['role'], name='publications_role_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='publicationprofessor',
            unique_together={('publication', 'professor'), ('publication', 'author_order')},
        ),
    ]
