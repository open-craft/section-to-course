section-to-course
#############################

|license-badge| |status-badge|

Purpose
*******

Allows course authors to factors sections from Open edX courses into their own new course.

Getting Started
***************

Developing
==========

One Time Setup
--------------
Set up the Open edX [devstack](https://github.com/openedx/devstack)

Then, in the `src` directory of your devstack, run:

.. code-block::
  git clone git@github.com:open-craft/section-to-course.git

Then, in your `devstack` directory, run:

.. code-block::
  make dev.shell.studio
  cd /edx/src/section-to-course
  pip install -e .

Running Tests
-------------

To run tests, within the studio shell, in `/edx/app/edxapp/edx-platform`, run:

.. code-block::
  DJANGO_SETTINGS_MODULE=cms.envs.test pytest --pyargs section_to_course --rootdir cms


License
*******

The code in this repository is licensed under the AGPL 3.0.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

Reporting Security Issues
*************************

Please do not report security issues in public. Please email help@opencraft.com.

.. |license-badge| image:: https://img.shields.io/github/license/openedx/section-to-course.svg
    :target: https://github.com/open-craft/section-to-course/blob/main/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
