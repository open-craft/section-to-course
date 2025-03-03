"""Factories for the section_to_course app."""

import factory
from factory.django import DjangoModelFactory
from xmodule.modulestore.tests.factories import BlockFactory, CourseFactory  # pylint: disable=import-error

from section_to_course.compat import update_outline_from_modulestore
from section_to_course.models import SectionToCourseLink


class SectionToCourseLinkFactory(DjangoModelFactory):
    """
    Factory for SectionToCourseLink.
    """
    source_course = factory.SubFactory(CourseFactory)
    source_course_id = factory.LazyAttribute(lambda obj: obj.source_course.id)
    source_section = factory.SubFactory(
        BlockFactory, parent=factory.SelfAttribute('..source_course'), category='chapter',
    )
    source_section_id = factory.LazyAttribute(lambda obj: obj.source_section.location)
    destination_course = factory.SubFactory(CourseFactory)
    destination_course_id = factory.LazyAttribute(lambda obj: obj.destination_course.id)
    destination_section = factory.SubFactory(
        BlockFactory, parent=factory.SelfAttribute('..destination_course'), category='chapter',
    )
    destination_section_id = factory.LazyAttribute(lambda obj: obj.destination_section.location)

    @classmethod
    def create(cls, **kwargs):
        """
        Create a SectionToCourseLink.
        """
        instance = super().create(**kwargs)
        if kwargs.get('source_course'):
            update_outline_from_modulestore(instance.source_course_id)
        if kwargs.get('destination_course'):
            update_outline_from_modulestore(instance.destination_course_id)
        return instance

    class Meta:
        """
        Configuration for SectionToCourseLinkFactory.
        """
        exclude = ('source_course', 'source_section', 'destination_section', 'destination_course')
        model = SectionToCourseLink
