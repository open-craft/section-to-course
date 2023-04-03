"""
Django command for converting a section into a course.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from section_to_course.utils import paste_from_template


User = get_user_model()


class Command(BaseCommand):
    """
    Management command to convert a section into a course.
    """

    help = 'Converts a section into a course'

    def add_arguments(self, parser):
        parser.add_argument('destination_course_id', type=str)
        parser.add_argument('section_id', type=str)
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        user = User.objects.get(username=options['username'])
        paste_from_template(
            destination_course_id=options['destination_course_id'],
            block_id=options['section_id'],
            user=user,
        )
        self.stdout.write(self.style.SUCCESS('Section copied successfully.'))
