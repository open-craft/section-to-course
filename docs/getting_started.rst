Getting Started
***************

Developing
==========

One Time Setup
--------------
1. Set up the Open edX `devstack <https://github.com/openedx/devstack>`_ using the `nutmeg.master` version as explained in `this guide <https://edx.readthedocs.io/projects/open-edx-devstack/en/latest/developing_on_named_release_branches.html>`_.

Then, in the ``edx-platform`` repository root, run:

.. code-block:: bash

    git remote add open-craft git@github.com:open-craft/edx-platform.git
    git fetch open-craft
    git checkout open-craft/opencraft-release/nutmeg.2

2. Then, in the ``src`` directory of your devstack, run:

.. code-block:: bash

    git clone git@github.com:open-craft/section-to-course.git

Then, in your `devstack` directory, run:

.. code-block:: bash

    make dev.shell.studio
    cd /edx/src/section-to-course
    pip install -e .
