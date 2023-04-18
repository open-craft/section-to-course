#!/usr/bin/env python
"""
Tests for the `section-to-course` models module.
"""
from django.test import TestCase

from section_to_course.models import SectionToCourseLink


class TestSectionToCourseLink(TestCase):
    """
    Tests of the SectionToCourseLink model.
    """

    def test_string(self):
        """Test string rendering of the model."""
        link = SectionToCourseLink.objects.create(
            source_course_id='course-v1:edX+DemoX+Demo_Course',
            destination_course_id='course-v1:OpenCraft+Tutorials+Basic_Questions',
            source_section_id='block-v1:edX+DemoX+Demo_Course+type@sequential+block@basic_questions',
        )
        assert str(link) == '<SectionToCourseLink #1, edX+DemoX+Demo_Course to ' \
                            'OpenCraft+Tutorials+Basic_Questions for basic_questions>'
