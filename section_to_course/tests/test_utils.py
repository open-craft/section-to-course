"""
Tests utility functions for section_to_course.
"""

from common.djangoapps.student.tests.factories import UserFactory
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, BlockFactory

from section_to_course.models import SectionToCourseLink
from section_to_course.utils import paste_from_template


class TestPasteFromTemplate(ModuleStoreTestCase):
    """
    Tests of the paste_from_template function.
    """

    def test_paste_from_template(self):
        """
        Test that the paste_from_template function works as expected.
        """
        source_course = CourseFactory()
        destination_course = CourseFactory()
        source_chapter = BlockFactory(parent=source_course, category='chapter', display_name='Source Chapter')
        user = UserFactory()
        paste_from_template(
            destination_course_id=str(destination_course.id),
            block_id=str(source_chapter.location),
            user=user,
        )
        link = SectionToCourseLink.objects.filter(
            source_course_id=source_course.id,
            destination_course_id=destination_course.id,
            source_section_id=source_chapter.location,
        ).first()
        assert link is not None
        store = modulestore()
        assert store.get_item(link.destination_section_id).display_name == 'Source Chapter'
        source_chapter.display_name = 'Revised source chapter'
        store.update_item(source_chapter, user.id)
        paste_from_template(
            destination_course_id=str(destination_course.id),
            block_id=str(source_chapter.location),
            user=user,
        )
        assert store.get_item(link.destination_section_id).display_name == 'Revised source chapter'
        assert SectionToCourseLink.objects.all().count() == 1
