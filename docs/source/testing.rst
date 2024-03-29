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

User Interface tests are developed using `cypress <https://www.cypress.io/>`_,
and the tests are developed for both Firefox and Chrome web browsers.

.. code-block:: console

    $ cd swift_browser_ui_frontend/
    $ npm install -g pnpm@8
    $ pnpm install
    $ pnpm run build
    $ cd  ..
    $ pnpm install cypress
    $ pnpm exec cypress open
