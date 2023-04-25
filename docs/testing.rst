.. _chapter-testing:

Testing
#######

section-to-course has an assortment of test cases and code quality
checks to catch potential problems during development.
Running Tests
-------------

To run tests, within the studio shell, in `/edx/src/section-to-course`, run:

.. code-block:: bash

    make test

.. code-block:: bash

    $ make validate

To run just the unit tests:

.. code-block:: bash

    $ make test

To run just the unit tests and check diff coverage

.. code-block:: bash

    $ make diff_cover

To run just the code quality checks:

.. code-block:: bash

    $ make quality

To run the unit tests under every supported Python version and the code
quality checks:

.. code-block:: bash

    $ make test-all

To generate and open an HTML report of how much of the code is covered by
test cases:

.. code-block:: bash

    $ make coverage
