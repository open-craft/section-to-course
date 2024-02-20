"""
Utility functions for section_to_course.
"""

from django.utils import timezone

from section_to_course.compat import (
    block_key_class,
    derive_key,
    duplicate_block,
    modulestore,
    not_found_exception,
    update_from_source,
)
from section_to_course.models import SectionToCourseLink


def paste_from_template(*, source_block_usage_key, destination_course_key, user):
    """
    Copy a block to a destination course.

    Given a source block_id and a destination course id, copy the block to
    the destination course, overwriting any previous copy of that
    block in the destination course. It will also copy over all the block's
    children and any files it determines to be related.
    """
    store = modulestore()
    destination_course = store.get_course(destination_course_key)
    if not destination_course:
        raise not_found_exception()(f'Course {destination_course_key} could not be found!')
    block_key = block_key_class()(source_block_usage_key.block_type, source_block_usage_key.block_id)
    block = store.get_item(source_block_usage_key)
    with store.bulk_operations(destination_course_key):
        destination_key = derive_key(destination_course_key, block_key, destination_course)
        destination_usage_key = destination_course_key.make_usage_key(
            destination_key.type, destination_key.id,
        )
        try:
            dest_block = store.get_item(destination_usage_key)
            update_from_source(source_block=block, destination_block=dest_block, user=user)
        except not_found_exception():
            dest_block_location = duplicate_block(
                destination_course=destination_course,
                source_block_usage_key=source_block_usage_key,
                user=user,
                destination_usage_key=destination_usage_key,
                block=block,
            )
            dest_block = store.get_item(dest_block_location)
        dest_block.children = store.copy_from_template(
            source_keys=block.children, dest_key=dest_block.scope_ids.usage_id, user_id=user.id,
        )
        store.publish(dest_block.scope_ids.usage_id, user.id)
    obj, _ = SectionToCourseLink.objects.update_or_create(
        source_course_id=source_block_usage_key.course_key,
        destination_course_id=destination_course_key,
        source_section_id=source_block_usage_key,
        defaults={
            'last_refresh': timezone.now(),
            # Not part of the unique constraint, so it must be in the defaults to
            # avoid triggering a constraint violation.
            'destination_section_id': dest_block.scope_ids.usage_id,
        },
    )
    return obj
