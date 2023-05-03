"""
Tests utility functions for section_to_course.
"""
from common.djangoapps.student.tests.factories import UserFactory
from django.utils import timezone
from freezegun import freeze_time
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

try:
    from xmodule.modulestore.tests.factories import BlockFactory, CourseFactory
except ImportError:
    # This is no longer needed in Palm.
    from xmodule.modulestore.tests.factories import ItemFactory as BlockFactory, CourseFactory

from section_to_course.models import SectionToCourseLink
from section_to_course.utils import paste_from_template

# TODO: Add CI capability. We need to rope in the platform to perform these tests.


class TestPasteFromTemplate(ModuleStoreTestCase):
    """
    Tests of the paste_from_template function.
    """

    @freeze_time('2023-01-01')
    def test_paste_from_template(self):
        """
        Test that the paste_from_template function works as expected.
        """
        source_course = CourseFactory()
        destination_course = CourseFactory()
        source_chapter = BlockFactory(parent=source_course, category='chapter', display_name='Source Chapter')
        user = UserFactory()
        paste_from_template(
            destination_course_key=destination_course.id,
            source_block_usage_key=source_chapter.location,
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
            destination_course_key=destination_course.id,
            source_block_usage_key=source_chapter.location,
            user=user,
        )
        item = store.get_item(link.destination_section_id)
        assert item.display_name == 'Revised source chapter'
        assert item.published_on == timezone.now()
        assert item.published_by == user.id
        assert SectionToCourseLink.objects.count() == 1
