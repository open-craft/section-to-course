"""
Utility functions for section_to_course.
"""

from django.utils import timezone

from cms.djangoapps.contentstore.views.block import update_from_source, duplicate_block
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locator import BlockUsageLocator

from section_to_course.models import SectionToCourseLink
from xmodule.modulestore.split_mongo import BlockKey
from xmodule.modulestore.store_utilities import derived_key


def paste_from_template(*, destination_course_id, block_id, user):
    """
    Copy a block to a destination course.

    Given a source block_id and a destination course id, copy the block to
    the destination course, overwriting any previous copy of that
    block in the destination course. It will also copy over all the block's
    children and any files it determines to be related.
    """
    store = modulestore()
    destination_course_key = CourseKey.from_string(destination_course_id)
    destination_course = store.get_course(destination_course_key)
    block_usage_key = BlockUsageLocator.from_string(block_id)
    block_key = BlockKey(block_usage_key.block_type, block_usage_key.block_id)
    block = store.get_item(block_usage_key)
    with store.bulk_operations(destination_course_key):
        destination_key = derived_key(destination_course_key, block_key, destination_course)
        destination_usage_key = destination_course_key.make_usage_key(
            destination_key.type, destination_key.id,
        )
        if store.has_item(destination_usage_key):
            dest_block = store.get_item(destination_usage_key)
            update_from_source(source_block=block, destination_block=dest_block, user_id=user.id)
        else:
            dest_block_location = duplicate_block(
                parent_usage_key=destination_course.location,
                duplicate_source_usage_key=block_usage_key,
                user=user,
                dest_usage_key=destination_usage_key,
                display_name=block.display_name,
                shallow=True,
            )
            dest_block = store.get_item(dest_block_location)
        dest_block.children = store.copy_from_template(
            source_keys=block.children, dest_key=dest_block.location, user_id=user.id,
        )
        store.publish(dest_block.location, user.id)
    SectionToCourseLink.objects.update_or_create(
        source_course_id=block_usage_key.course_key,
        destination_course_id=destination_course_key,
        source_section_id=block_usage_key,
        destination_section_id=dest_block.location,
        defaults={'last_refresh': timezone.now()},
    )
