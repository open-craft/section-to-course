# Generated by Django 3.2.23 on 2023-11-15 10:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('section_to_course', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectiontocourselink',
            name='last_refresh',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]