# Generated by Django 3.2.18 on 2023-04-13 20:30

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SectionToCourseLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('source_course_id', opaque_keys.edx.django.models.CourseKeyField(db_index=True, max_length=255, null=False, blank=False)),
                ('destination_course_id', opaque_keys.edx.django.models.CourseKeyField(db_index=True, max_length=255, null=False, blank=False)),
                ('source_section_id', opaque_keys.edx.django.models.UsageKeyField(db_index=True, max_length=255, null=False, blank=False)),
                ('destination_section_id', opaque_keys.edx.django.models.UsageKeyField(db_index=True, max_length=255, null=False, blank=False)),
                ('last_refresh', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'unique_together': {('source_course_id', 'destination_course_id', 'source_section_id')},
            },
        ),
    ]
