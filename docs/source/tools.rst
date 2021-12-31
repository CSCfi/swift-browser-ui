Tools used in project
=====================

Backend
-------
The backend is written in Python, requiring at minimum Python version `3.6.8`,
but is tested with 3.7 and 3.8 as well. Additionally the following libraries are used
in the program development:

* `aiohttp for the API server <https://aiohttp.readthedocs.io/en/stable/>`_
* `uvloop for increasing server performance <https://uvloop.readthedocs.io/>`_
* `keystoneauth1 for authenticating with Openstack <https://docs.openstack.org/keystoneauth/latest/>`_
* `python-swiftclient for communicating with Openstack Swift API <https://docs.openstack.org/python-swiftclient/latest/>`_
* `cryptography for encrypting session cookies <https://docs.openstack.org/python-swiftclient/latest/>`_
* `click for quickly providing a CLI for the server <https://click.palletsprojects.com/en/7.x/>`_

Frontend
--------
The frontend is written as an SPA (Single Page Application), in *ES6*
Javascript. The frontend code is not tested for cross-compilation to ES5. The
following libraries are used in writing the frontend:

* `Vue.js for site functionality and DOM manipulation <https://vuejs.org/>`_
* `Vue router for site routing support <https://router.vuejs.org/>`_
* `Vue i18n for language support <https://router.vuejs.org/>`_
* `Buefy for site styling and components <https://buefy.org/>`_
* `Buefy also comes with bulma for css framework <https://bulma.io/>`_
* `Lodash for mostly debouncing functions to improve responsivity <https://lodash.com/>`_

Tests
-----
Tests are written to be run with `Pytest <https://docs.pytest.org/en/latest/>`_. The following libraries are used in
writing the tests:

* `tox for test automation <https://tox.readthedocs.io/en/latest/>`_
* `cypress for UI test automation <https://www.cypress.io/>`_
* `pytest-timeout for timing out UI tests, which can hang when failing <https://pypi.org/project/pytest-timeout/1.2.1/>`_

UI tests also require the WebDrivers for Chrome and Firefox, if tests are to
be run locally.

* `WebDriver for Chrome <https://chromedriver.chromium.org/>`_
* `WebDriver for Firefox <https://github.com/mozilla/geckodriver/releases>`_

Documentation
-------------

The documentation is automatically built with `sphinx <http://www.sphinx-doc.org/en/master/>`_

Charts
~~~~~~
The charts in documentation are made with `Dia <http://dia-installer.de/doc/en/index.html>`_. The program is old
fashioned, but versatile and can be installed without adding repositories,
with the added benefit of not requiring the use of browser toools for making
the charts. Charts are located in ``docs/charts``, and the exported vector
graphics file is linked into the documentation image directory.
