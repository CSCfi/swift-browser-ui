Testing
=======

.. note:: Unit tests and integration tests are automatically executed with every PR

Unit Testing
------------

In order to run the unit tests, security checks with `bandit <https://github.com/PyCQA/bandit>`_,
Sphinx documentation check for links consistency and HTML output
and `flake8 <http://flake8.pycqa.org/en/latest/>`_ (coding style guide)
`tox <http://tox.readthedocs.io/>`_. To run the unit tests and UI tests in parallel use:

.. code-block:: console

    $ tox -p auto

To run environments seprately use:

.. code-block:: console

    $ # list environments
    $ tox -l
    $ # run flake8
    $ tox -e flake8
    $ # run bandit
    $ tox -e bandit
    $ # run docs
    $ tox -e docs


User Interface Testing
----------------------

User Interface tests are developed using `Selenium Webdriver <https://selenium-python.readthedocs.io>`_,
and the tests are developed for both Firefox and Chrome web browsers.
When using `tox` the UI tests are run using a headless browser and this is set by the environment
variable ``TEST_ENABLE_HEADLESS`` to any value.

.. code-block:: console

    $ tox -l
    $ # run UI tests in firefox
    $ tox -e firefox
    $ # run UI tests in chrome
    $ tox -e chrome

UI Screenshots
~~~~~~~~~~~~~~

We provide an utility for generating UI screenshots based on the functions implemented in
the UI testing scenarios. The utility can be run using:

.. code-block:: console

    $ python -m ui_tests.ui_take_screenshots
