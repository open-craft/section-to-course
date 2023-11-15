Change Log
##########

..
   All enhancements and patches to section_to_course will be documented
   in this file. It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

[0.4.2] - 2023-11-15
********************

Changed
=======

* Upgraded tox from ``v3`` to ``v4`` and removed ``tox-battery``.

Added
=====

* Created a new test for missing migrations and added it to the CI.

Fixed
=====

* Added a missing Django migration.
* Replaced the invalid ``ROOT_URLCONF`` in ``test_settings.py``.
* Made ``./manage.py`` executable.

[0.4.1] - 2023-11-07
********************

Fixed
=====

* Compatibility of ``compat`` imports with Palm.

[0.4.0] - 2023-05-18
********************

Changed
=======

* Removed course autocomplete for performance reasons. Source courses must now be specified by course key pasted into the source course ID field.

Added
=====

* Github integration-tests action.

[0.3.0] - 2023-05-12
********************

Changed
=======

* New section-based courses are self-paced.

[0.2.0] - 2023-05-10
********************

Added
=====

* Admin views for creating new section-based courses.
* First release on PyPI.

[0.1.0] - 2023-04-03
********************

Added
=====

* Initial section-derived course creation code.
