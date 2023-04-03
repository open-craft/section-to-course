section-to-course
#############################

|pypi-badge| |ci-badge| |codecov-badge|
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
.. code-block::

  # Clone the repository
  git clone git@github.com:open-craft/section-to-course.git
  cd section-to-course

  # Set up a virtualenv using virtualenvwrapper with the same name as the repo and activate it
  mkvirtualenv -p python3.8 section-to-course


Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  workon section-to-course

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make validate

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.

Deploying
=========

This application must be installed and added to the INSTALLED_APPS in the LMS.

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

.. |pypi-badge| image:: https://img.shields.io/pypi/v/section-to-course.svg
    :target: https://pypi.python.org/pypi/section-to-course/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/open-craft/section-to-course/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/open-craft/section-to-course/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/open-craft/section-to-course/coverage.svg?branch=main
    :target: https://codecov.io/github/openedx/section-to-course?branch=main
    :alt: Codecov

.. |license-badge| image:: https://img.shields.io/github/license/openedx/section-to-course.svg
    :target: https://github.com/open-craft/section-to-course/blob/main/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
