"""
Tests for the API views of section_to_course.
"""

# pylint: disable=no-self-use
from common.djangoapps.student.tests.factories import UserFactory, TEST_PASSWORD
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from section_to_course.compat import update_outline_from_modulestore
from section_to_course.tests.factories import SectionToCourseLinkFactory

try:
    from xmodule.modulestore.tests.factories import BlockFactory, CourseFactory
except ImportError:
    from xmodule.modulestore.tests.factories import CourseFactory
    from xmodule.modulestore.tests.factories import ItemFactory as BlockFactory


def create_subsections():
    """Create some subsections."""
    course = CourseFactory(display_name='Demo Course', org='edX', course='DemoX')
    experimentation = BlockFactory(parent=course, category='chapter', display_name='Experimentation')
    postulation = BlockFactory(parent=course, category='chapter', display_name='Postulation')
    elucidation = BlockFactory(parent=course, category='chapter', display_name='Elucidation')
    # Have to call this manually since the factories don't.
    update_outline_from_modulestore(course.id)
    return {
        'course': course,
        'experimentation': experimentation,
        'postulation': postulation,
        'elucidation': elucidation,
    }


class TestSectionAutoCompleteAPI(ModuleStoreTestCase, APITestCase):
    """
    Tests for the section autocomplete API.
    """

    def test_rejects_unauthenticated(self):
        """
        Test that the API rejects unauthenticated users.
        """
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'course-v1:edX+DemoX+Demo_Course'})
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_rejects_unauthorized(self):
        """
        Test that the API rejects unauthorized users.
        """
        user = UserFactory.create()
        assert self.client.login(username=user.username, password=TEST_PASSWORD)
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'course-v1:edX+DemoX+Demo_Course'})
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_rejects_malformed(self):
        """
        Test that the API rejects malformed course IDs.
        """
        user = UserFactory.create(is_staff=True)
        assert self.client.login(username=user.username, password=TEST_PASSWORD)
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'malarkey'})
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_handles_nonexistent(self):
        """
        Test that the API rejects malformed course IDs.
        """
        user = UserFactory.create(is_staff=True)
        assert self.client.login(username=user.username, password=TEST_PASSWORD)
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'course-v1:edX+DemoX+Demo_Course'}),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_handles_blank(self):
        """
        Test that blank terms return all sections.
        """
        user = UserFactory.create(is_staff=True)
        assert self.client.login(username=user.username, password=TEST_PASSWORD)
        create_subsections()
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'course-v1:edX+DemoX+Demo_Course'}),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Experimentation', 'text': 'Experimentation'},
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Postulation', 'text': 'Postulation'},
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Elucidation', 'text': 'Elucidation'}],
        }

    def test_filters_existing(self):
        """
        Test that autocomplete filters existing sections.
        """
        user = UserFactory.create(is_staff=True)
        assert self.client.login(username=user.username, password=TEST_PASSWORD)
        section_data = create_subsections()
        SectionToCourseLinkFactory(source_course=section_data['course'], source_section=section_data['experimentation'])
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'course-v1:edX+DemoX+Demo_Course'})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Postulation', 'text': 'Postulation'},
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Elucidation', 'text': 'Elucidation'}],
        }

    def test_filters_names(self):
        """
        Test that autocomplete filters names.
        """
        user = UserFactory.create(is_staff=True)
        assert self.client.login(username=user.username, password=TEST_PASSWORD)
        create_subsections()
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'course-v1:edX+DemoX+Demo_Course'})
            + '?term=e',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Experimentation', 'text': 'Experimentation'},
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Elucidation', 'text': 'Elucidation'}],
        }

    def test_filters_keys(self):
        """
        Test that autocomplete filters keys.
        """
        user = UserFactory.create(is_staff=True)
        assert self.client.login(username=user.username, password=TEST_PASSWORD)
        create_subsections()
        response = self.client.get(
            reverse('section_to_course:section_autocomplete', kwargs={'course_id': 'course-v1:edX+DemoX+Demo_Course'})
            + '?term=block-v1%3AedX%2BDemoX%2BDemo_Course%2Btype%40chapter%2Bblock%40e',
            )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'results': [
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Experimentation', 'text': 'Experimentation'},
                {'id': 'block-v1:edX+DemoX+Demo_Course+type@chapter+block@Elucidation', 'text': 'Elucidation'}],
        }
