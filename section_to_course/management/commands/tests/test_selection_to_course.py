"""
Tests the SectionToCourse management command
"""
from io import StringIO

from common.djangoapps.student.tests.factories import UserFactory
from django.core.management import call_command

try:
    from xmodule.modulestore.tests.factories import BlockFactory, CourseFactory
except ImportError:
    # This is no longer needed in Palm.
    from xmodule.modulestore.tests.factories import ItemFactory as BlockFactory, CourseFactory

from xmodule.modulestore.tests.utils import MixedSplitTestCase

from section_to_course.models import SectionToCourseLink


class TestSectionToCourseCommand(MixedSplitTestCase):
    """
    Tests for the section_to_course management command.
    """
    maxDiff = None

    def setUp(self):
        """
        Set up the tests.
        """
        super().setUp()
        self.source_course = CourseFactory()
        self.destination_course = CourseFactory()
        self.source_chapter = BlockFactory(parent=self.source_course, category='chapter', display_name='Source Chapter')
        self.user = UserFactory()

    def test_command(self):
        """
        Test that the command works as expected.
        """
        source_course = CourseFactory()
        destination_course = CourseFactory()
        source_chapter = BlockFactory(parent=source_course, category='chapter', display_name='Source Chapter')
        call_command(
            'section_to_course',
            str(source_chapter.location),
            str(destination_course.id),
            self.user.username,
        )
        SectionToCourseLink.objects.get(
            source_course_id=source_course.id,
            destination_course_id=destination_course.id,
            source_section_id=source_chapter.location,
        )

    def test_handles_nonexistent_user(self):
        """
        Test that the command handles a nonexistent user gracefully.
        """
        stderr = StringIO()
        with self.assertRaises(SystemExit) as exc:
            call_command(
                'section_to_course',
                str(self.source_chapter.location),
                str(self.destination_course.id),
                'BogusUser',
                stderr=stderr,
            )
            self.assertEqual(exc.exception.code, 1)
        assert stderr.getvalue() == 'User "BogusUser" does not exist.\n'

    def test_handles_bad_course_key(self):
        """
        Test that the command handles a bad course key gracefully.
        """
        stderr = StringIO()
        with self.assertRaises(SystemExit) as exc:
            call_command(
                'section_to_course',
                str(self.source_chapter.location),
                'bogus',
                self.user.username,
                stderr=stderr,
            )
            self.assertEqual(exc.exception.code, 1)
        assert stderr.getvalue() == '"bogus" is not a valid course key.\n'

    def test_handles_bad_usage_key(self):
        """
        Test that the command handles a bad usage key gracefully.
        """
        stderr = StringIO()
        with self.assertRaises(SystemExit) as exc:
            call_command(
                'section_to_course',
                'bogus',
                str(self.destination_course.id),
                self.user.username,
                stderr=stderr,
            )
            self.assertEqual(exc.exception.code, 3)
        assert stderr.getvalue() == '"bogus" is not a valid block usage key.\n'

    def test_handles_not_found(self):
        """
        Test that the command handles a not found error gracefully.
        """
        stderr = StringIO()
        with self.assertRaises(SystemExit) as exc:
            call_command(
                'section_to_course',
                str(self.source_chapter.location),
                str(self.destination_course.id) + '1',
                self.user.username,
                stderr=stderr,
            )
            self.assertEqual(exc.exception.code, 4)
        assert stderr.getvalue() == f'Course {self.destination_course.id}1 could not be found!\n'
