Technical documentation
=======================
The technologies used are documented here, with a sprinkle of useful resources
to ease in the understanding of the project code. Code itself tries to be
commented as necessary, but if something doesn't seem comprehensible by
reading, adding an issue about insufficient documentation is most welcome.

Style
-----

.. note::
    This list can be updated as necessary.

Preferred coding style is already located also in the contribution guidelines
but as a recap:

    * Indentation should be 4 *spaces*, besides html, for which it's 2
    * 80 character limit is almost strict, but

        - Can be broken in documentation when hyperlinks go over the limits
        - Can be broken in html files
        - Can be broken in js files, but only in html templates

    * Python

        - PEP8 and PEP257 are followed with small variations
        - Lines are broken after logical operators, not before
        - Function names mostly follow established conventions
        - Multiline docstring has a newline after quote marks

    * Javascript

        - Function names use camelCase
        - Opening brace goes on the line of definition
        - All statements that can, should end with a semicolon ``;``, even
          when not strictly required
        - Code should work in browser as-is, no compilation or building
          required
        - Vue templates intentionally break indentation to improve
          readability (by starting from bottom indentation level)
        - Use template strings for multiline strings

    * HTML (also concerns HTML templates in Javascript)

        - Each attribute should go on their own line if there are more than
          two attributes present

About login process
-------------------
The program uses the WebSSO support provided by Openstack, when the support
has been implemented. At minimum the program requires the Openstack instance
that it's supposed to be used with to implement the federated authentication,
in which the non-WebSSO token delivery method can be used.

A collection of links to provide a recap of the things necessary to know about
Openstack WebSSO implementation:

* `Federated authentication API in Openstack <https://docs.openstack.org/keystone/pike/advanced-topics/federation/federated_identity.html>`_
* `WebSSO details conveniently explained (or how it works in the OS Horizon dashboard) <http://www.gazlene.net/demystifying-keystone-federation.html>`_
* `Openstack Horizon dahsboard WebSSO guide <https://docs.openstack.org/keystone/pike/advanced-topics/federation/websso.html>`_

The login process follows an *almost ordinary* process of federated
authentication with SAML, but that is something we don't need to concern
ourselves with – Openstack identity API takes care of that. The manual
version works in much the same way, but the user is required to copy and
paste the token themselves, since Openstack refuses to redirect to untrusted
platforms.

.. figure:: ./_static/images/WebSSO_login.svg
    :scale: 66%
    :alt: Sequence diagram of the login process
    :align: center

    Sequence diagram of the login process.

Backend
-------
Tool recap
~~~~~~~~~~
The backend is written in Python, requiring at minimum Python version `3.6.8`.
Additionally the following libraries are used in the program development:

* `aiohttp for the API server <https://aiohttp.readthedocs.io/en/stable/>`_
* `uvloop for increasing server performance <https://uvloop.readthedocs.io/>`_
* `keystoneauth1 for authenticating with Openstack <https://docs.openstack.org/keystoneauth/latest/>`_
* `python-swiftclient for communicating with Openstack Swift API <https://docs.openstack.org/python-swiftclient/latest/>`_
* `cryptography for encrypting session cookies <https://docs.openstack.org/python-swiftclient/latest/>`_
* `click for quickly providing a CLI for the server <https://click.palletsprojects.com/en/7.x/>`_

Frontend
--------
Tool recap
~~~~~~~~~~
The frontend is written as an SPA, in *ES6* Javascript. The frontend code is
not tested for cross-compilation to ES5. The following libraries are used in
writing the frontend:

* `Vue.js for site functionality and DOM manipulation <https://vuejs.org/>`_
* `Vue router for site routing support <https://router.vuejs.org/>`_
* `Vue i18n for language support <https://router.vuejs.org/>`_
* `Buefy for site styling and components <https://buefy.org/>`_
* `Buefy also comes with bulma for css framework <https://bulma.io/>`_
* `Lodash for mostly debouncing functions to improve responsivity <https://lodash.com/>`_

API
---
.. hint::
    The API has several endpoints, which are documented here. The API can
    also be used with the convenience functions, located in the ``api.js``
    file.

.. note::
    All API queries expect an open session to Openstack, which meas the
    queries towards Openstack are correctly scoped to the open project
    without further information in the API query. This of course requires
    a valid session token to be present with every API call.

The following flowchart gives a generic image of the possible responses from
the API during normal usage.

.. figure:: ./_static/images/API_flow.svg
    :scale: 50%
    :alt: Flowchart of the simplified API execute routes.
    :align: center

    Flowchart of the simplified API execute routes upon query.

/api/username
~~~~~~~~~~~~~

.. code-block::

    The API endpoint for querying the Openstack username.

    Query string:
        None

    Returns:
        JSON response containing the User ID in a plain string.

/api/projects
~~~~~~~~~~~~~

.. code-block::

    The API endpoint for querying the Openstack projects that are available
    for the user.

    Query string:
        None

    Returns:
        JSON respone containing a list of the available projects as objects,
        the object containing the project name and ID.

/api/active
~~~~~~~~~~~

.. code-block::

    The API endpoint for querying the project that the authentication token
    is currently scoped for.

    Query string:
        None

    Returns:
        JSON response containing an object, containing the project name and
        ID.

/api/get-project-meta
~~~~~~~~~~~~~~~~~~~~~

.. code-block::

    The API endpoint for querying the project metadata, e.g. project storage
    usage and object count etc.

    Query string:
        None

    Returns:
        JSON response containing the project metadata.

/api/buckets
~~~~~~~~~~~~

.. code-block::

    The API endpoint for querying all the containers in a project.

    Query string:
        None

    Returns:
        JSON response containing a list of objects, each containing the
        container name, object count and total size in bytes.

/api/objects
~~~~~~~~~~~~

.. code-block::

    The API endpoint for querying all the objects in a container.

    Query string:
        ?bucket=CONTAINER

    Returns:
        JSON response containing a list of objects, each containing the
        object name, ETag hash, size in bytes and the date of last
        modification.

/api/dload
~~~~~~~~~~

.. code-block::

    The API endpoint for getting a redirection to a working temprary download
    link directly to the storage backend.

    Query string:
        ?bucket=CONTAINER&objkey=OBJECTNAME

    Returns:
        HTTP302 redirection to the correct download address.

/api/meta
~~~~~~~~~

.. code-block::

    The API endpoint for querying container or object metadata. The API
    handles the parsing of S3 generated metadata into a usable form.
    When querying multiple objects, the objects can be separated by a comma.

    Query string:
        ?container=CONTAINER or ?container=CONTAINER&object=[OBJECTNAMES]

    Returns:
        JSON response containing either an object containing container
        metadata in full, or a list containing the object metadata in
        objects.

Tests
-----
Tool recap
~~~~~~~~~~
Tests are written to be run with `Pytest <https://docs.pytest.org/en/latest/>`_. The following libraries are used in
writing the tests:

* `tox for test automation <https://tox.readthedocs.io/en/latest/>`_
* `selenium-python for UI test automation <https://selenium-python.readthedocs.io/>`_
* `asynctest for implementing async testing with TestCase class <https://asynctest.readthedocs.io/en/latest/>`_
* `pytest-timeout for timing out UI tests, which can hang when failing <https://pypi.org/project/pytest-timeout/1.2.1/>`_

UI tests also require the WebDrivers for Chrome and Firefox, if tests are to
be run locally.

* `WebDriver for Chrome <https://chromedriver.chromium.org/>`_
* `WebDriver for Firefox <https://github.com/mozilla/geckodriver/releases>`_

Documentation
-------------

Builds
~~~~~~
The documentation is automatically built with `sphinx <http://www.sphinx-doc.org/en/master/>`_

Screenshots
~~~~~~~~~~~
Selenium and the test server are also used for automating the documentation
screenshots.

Charts
~~~~~~
The charts in documentation are made with `Dia <http://dia-installer.de/doc/en/index.html>`_. The program is old
fashioned, but versatile and can be installed without adding repositories,
with the added benefit of not requiring the use of browser toools for making
the charts. Charts are located in ``docs/charts``, and the exported vector
graphics file is linked into the documentation image directory.
