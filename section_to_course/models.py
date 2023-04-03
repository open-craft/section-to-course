"""
Database models for section_to_course.
"""
# from django.db import models
from django.db import models
from model_utils.models import TimeStampedModel
from opaque_keys.edx.django.models import CourseKeyField, UsageKeyField


class SectionToCourseLink(TimeStampedModel):
    """
    A model that links a section to a course.

    .. no_pii:
    """

    source_course_id = CourseKeyField(max_length=255, db_index=True, null=False, blank=False)
    destination_course_id = CourseKeyField(max_length=255, db_index=True, null=False, blank=False)
    source_section_id = UsageKeyField(max_length=255, db_index=True, null=False, blank=False)
    destination_section_id = UsageKeyField(max_length=255, db_index=True, null=False, blank=False)
    last_refresh = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta settings for SectionToCourseLink model."""

        unique_together = ('source_course_id', 'destination_course_id', 'source_section_id')

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return f'<SectionToCourseLink #{self.id}, {str(self.source_course_id).split(":")[-1]} to ' \
               f'{str(self.destination_course_id).split(":")[-1]} for {str(self.source_section_id).split("@")[-1]}>'
