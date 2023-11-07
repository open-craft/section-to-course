"""
Tests for the admin views of the section_to_course app.
"""
from common.djangoapps.student.tests.factories import TEST_PASSWORD, UserFactory  # pylint: disable=import-error
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from opaque_keys.edx.locator import CourseLocator
from organizations.tests.factories import OrganizationFactory
from rest_framework import status
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase  # pylint: disable=import-error

from ..compat import get_course, update_outline_from_modulestore
from ..models import SectionToCourseLink
from .factories import SectionToCourseLinkFactory

try:
    from xmodule.modulestore.tests.factories import BlockFactory, CourseFactory
except ImportError:
    from xmodule.modulestore.tests.factories import CourseFactory
    from xmodule.modulestore.tests.factories import ItemFactory as BlockFactory


class TestSectionToCourseLinkAdmin(ModuleStoreTestCase, TestCase):
    """
    Tests for the admin views.
    """

    def setUp(self):
        """Set up our admin test cases."""
        super().setUp()
        user = UserFactory.create(is_staff=True, is_superuser=True)
        self.client.login(username=user.username, password=TEST_PASSWORD)

    def test_listing(self):
        """Test that the admin listing page loads."""
        SectionToCourseLinkFactory()
        SectionToCourseLinkFactory(destination_course=None, destination_course_id=CourseLocator('foo', 'bar', 'baz'))
        response = self.client.get(reverse('admin:section_to_course_sectiontocourselink_changelist'))
        assert response.status_code == status.HTTP_200_OK
        assert '>edit course<' in response.content.decode('utf-8')

    def test_detail(self):
        """Test that the admin detail page loads."""
        link = SectionToCourseLinkFactory()
        response = self.client.get(reverse('admin:section_to_course_sectiontocourselink_change', args=[link.id]))
        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode('utf-8')
        assert '>edit course<' in content
        assert 'Last refresh:' in content

    @freeze_time('2018-01-01')
    def test_refresh_from_changelist(self):
        """Test that the admin refresh action on the changelist works."""
        link = SectionToCourseLinkFactory()
        original_time = timezone.now()
        assert link.last_refresh == original_time
        with freeze_time('2023-01-01'):
            response = self.client.post(
                reverse('admin:section_to_course_sectiontocourselink_changelist'), {
                    'action': 'refresh_courses',
                    '_selected_action': str(link.id),
                    'index': '0',
                    'select_across': '0',
                },
                follow=True,
            )
            new_time = timezone.now()
        assert response.status_code == status.HTTP_200_OK
        link.refresh_from_db()
        assert link.last_refresh == new_time
        assert link.last_refresh != original_time

    @freeze_time('2018-01-01')
    def test_refresh_from_change(self):
        """Test that the admin refresh button works."""
        link = SectionToCourseLinkFactory()
        original_time = timezone.now()
        assert link.last_refresh == original_time
        with freeze_time('2023-01-01'):
            response = self.client.post(
                reverse(
                    'admin:section_to_course_sectiontocourselink_actions',
                    kwargs={'pk': link.id, 'tool': 'refresh_this'}
                ),
                follow=True,
            )
            new_time = timezone.now()
        assert response.status_code == status.HTTP_200_OK
        link.refresh_from_db()
        assert link.last_refresh == new_time
        assert link.last_refresh != original_time

    def create_section_to_course_link(self, course, section, org):
        """Create a section to course link via the admin."""
        return self.client.post(
            reverse('admin:section_to_course_sectiontocourselink_add'), {
                'source_course_id': str(course.id),
                'source_section_id': str(section.location),
                'new_course_name': 'New Course',
                'new_course_org': org.short_name,
                'new_course_number': 'NC101',
                'new_course_run': '2023',
            },
            follow=True,
        )

    def test_create_course(self):
        """Test that filling out the form does create a course and a link."""
        course = CourseFactory()
        section = BlockFactory(parent_location=course.location)
        org = OrganizationFactory()
        update_outline_from_modulestore(course.id)
        response = self.create_section_to_course_link(course, section, org)
        assert response.status_code == status.HTTP_200_OK
        link = SectionToCourseLink.objects.get()
        assert link.source_course_id == course.id
        assert link.source_section_id == section.location
        update_outline_from_modulestore(link.destination_course_id)
        dest_course = get_course(link.destination_course_id)
        assert dest_course.title == 'New Course'
        assert dest_course.self_paced
        # Should not create a new link if it's already made.
        response = self.create_section_to_course_link(course, section, org)
        assert 'A course with this number, org, and run already exists.' in response.content.decode('utf-8')
        # Will throw if there's more than one.
        SectionToCourseLink.objects.get()
