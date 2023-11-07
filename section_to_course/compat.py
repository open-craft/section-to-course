"""
Functions for use in section_to_course which pull from the platform.

Functions here should normalize any changes from upstream, so that the rest of the app can
depend on them rather than upstream's functions.
"""
# pylint: disable=import-error, import-outside-toplevel
from opaque_keys.edx.locator import CourseLocator
from organizations.api import get_organizations


def create_course(
    *,
    user,
    org: str,
    number: str,
    run: str,
    display_name: str,
    self_paced: bool = False,
):
    """
    Create a course to match a specific course key.
    """
    # Defer this import to avoid invoking cms startup code during module import.
    from cms.djangoapps.contentstore.views.course import create_new_course
    return create_new_course(
        user,
        org=org,
        number=number,
        run=run,
        fields={'display_name': display_name, 'self_paced': self_paced},
    )


def organization_options():
    """
    Return a Django choice tuple of organizations that can be used to create a course.
    """
    return (
        ('', '---'),
        *tuple((organization['short_name'], organization['name']) for organization in get_organizations()),
    )


def course_exists(course_key: CourseLocator) -> bool:
    """
    Check if a course exists.
    """
    return modulestore().has_course(course_key)


def get_course(course_key: CourseLocator):
    """
    Get a course from the modulestore.
    """
    return get_course_outline(course_key)


def modulestore():
    """
    Get the modulestore function from upstream.
    """
    from xmodule.modulestore.django import modulestore as upstream_modulestore
    return upstream_modulestore()


def not_found_exception():
    """
    Get the ItemNotFoundError exception from upstream.
    """
    from xmodule.modulestore.exceptions import ItemNotFoundError
    return ItemNotFoundError


def block_key_class():
    """
    Get the BlockKey class from upstream.
    """
    from xmodule.modulestore.split_mongo import BlockKey
    return BlockKey


def duplicate_block(
    *,
    destination_course,
    source_block_usage_key,
    user,
    destination_usage_key,
    block,
):
    """
    Duplicate a block using the upstream function.
    """
    try:
        # Quince and newer
        from cms.djangoapps.contentstore.utils import duplicate_block as upstream_duplicate_block
    except ImportError:
        try:
            # Palm
            from cms.djangoapps.contentstore.views.block import duplicate_block as upstream_duplicate_block
        except ModuleNotFoundError:
            # Nutmeg
            from cms.djangoapps.contentstore.views.item import duplicate_block as upstream_duplicate_block
    return upstream_duplicate_block(
        parent_usage_key=destination_course.location,
        duplicate_source_usage_key=source_block_usage_key,
        user=user,
        dest_usage_key=destination_usage_key,
        display_name=block.display_name,
    )


def update_from_source(
    *,
    source_block,
    destination_block,
    user,
):
    """
    Update a block's attributes from a source block. See upstream function.
    """
    try:
        # Quince and newer
        from cms.djangoapps.contentstore.utils import update_from_source as upstream_update_from_source
    except ImportError:
        try:
            # Palm
            from cms.djangoapps.contentstore.views.block import update_from_source as upstream_update_from_source
        except ModuleNotFoundError:
            # Nutmeg
            from cms.djangoapps.contentstore.views.item import update_from_source as upstream_update_from_source
    upstream_update_from_source(
        source_block=source_block, destination_block=destination_block, user_id=user.id,
    )


def derived_key(destination_course_key, block_key, destination_course):
    """
    Get the derived ID for a block duplicated from a source block. See upstream function.
    """
    from xmodule.modulestore.store_utilities import derived_key as upstream_derived_key
    return upstream_derived_key(
        destination_course_key,
        block_key,
        destination_course,
    )


def get_course_outline(course_key: CourseLocator):
    """
    Get the course outline for a course. See upstream function.
    """
    from openedx.core.djangoapps.content.learning_sequences.api import get_course_outline as upstream_get_course_outline
    return upstream_get_course_outline(course_key)


def update_outline_from_modulestore(course_key: CourseLocator):
    """
    Update the course outline for a course. See upstream function.

    This function is only used in tests, presently, since the course outline is updated
    via signals in the platform, which aren't activated during tests.
    """
    from cms.djangoapps.contentstore.tasks import \
        update_outline_from_modulestore as upstream_update_outline_from_modulestore
    return upstream_update_outline_from_modulestore(course_key)


def sequence_does_not_exist_exception():
    """
    Get the SequenceDoesNotExist exception from upstream.
    """
    from openedx.core.djangoapps.content.learning_sequences.data import ObjectDoesNotExist
    return ObjectDoesNotExist
