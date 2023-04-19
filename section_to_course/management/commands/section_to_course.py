"""
Django command for converting a section into a course.
"""
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import BlockUsageLocator
from xmodule.modulestore.exceptions import ItemNotFoundError

from section_to_course.utils import paste_from_template

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to convert a section into a course.
    """

    help = 'Converts a section into a course'

    def add_arguments(self, parser):
        parser.add_argument('source_section_id', type=str)
        parser.add_argument('destination_course_id', type=str)
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User "{options["username"]}" does not exist.'))
            sys.exit(1)
        try:
            destination_course_key = CourseKey.from_string(options['destination_course_id'])
        except InvalidKeyError:
            self.stderr.write(self.style.ERROR(f'"{options["destination_course_id"]}" is not a valid course key.'))
            sys.exit(2)
        try:
            source_block_usage_key = BlockUsageLocator.from_string(options['source_section_id'])
        except InvalidKeyError:
            self.stderr.write(self.style.ERROR(f'"{options["source_section_id"]}" is not a valid block usage key.'))
            sys.exit(3)
        try:
            paste_from_template(
                destination_course_key=destination_course_key,
                source_block_usage_key=source_block_usage_key,
                user=user,
            )
        except ItemNotFoundError as err:
            self.stderr.write(self.style.ERROR(str(err)))
            sys.exit(4)
        self.stdout.write(self.style.SUCCESS('Section copied successfully.'))
