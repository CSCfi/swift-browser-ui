.. _setup:

Setup Instructions
==================


The program can be installed with pip from the git repository:

.. code-block:: console

    # Requires python >= 3.6
    git clone git@github.com:CSCfi/swift-browser-ui.git
    pip install .


Environment Setup
-----------------

.. hint:: The command line arguments can also be configured as environment variables,
          the environment variable syntax is documented in the python click
          documentation [#]_ , the shape of a variable could take the following forms:


          * ``BROWSER_$ARGUMENT`` - affects every command;
          * ``BROWSER_$SUBCOMMAND_$ARGUMENT`` - affects subcommands e.g. ``start``, ``install``.

Variables are depicted in the table below:

+--------------------------------------+----------+-------------------------------------------------------------------------+
| ENV                                  | Default  | Description                                                             |
+--------------------------------------+----------+-------------------------------------------------------------------------+
| ``BROWSER_START_AUTH_ENDPOINT_URL``  |          | Authentication endpoint. Address for OpenStack keystone API ``v3``.     |
+--------------------------------------+----------+-------------------------------------------------------------------------+
| ``BROWSER_START_PORT``               | ``8080`` |                                                                         |
+--------------------------------------+----------+-------------------------------------------------------------------------+
| ``BROWSER_START_SET_ORIGIN_ADDRESS`` |          | Authentication return address, to which the ``WebSSO`` redirects.       |
+--------------------------------------+----------+-------------------------------------------------------------------------+

.. hint:: Authentication endpoint can also be specified with any openrc file,
          which can be usually downloaded from Openstack. The setup script
          from Openstack might ask for your password, but this isn't a
          required input and can be left empty.

Example environment variable files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the Pouta test environment with NGINX TLS termination proxy in use::

    export BROWSER_START_AUTH_ENDPOINT_URL="https://pouta-test.csc.fi:5001/v3"
    export BROWSER_START_PORT="8081"
    export BROWSER_START_SET_ORIGIN_ADDRESS="https://vm1950.kaj.pouta.csc.fi:8080/login/websso"

For the Pouta production environment for testing unsecurely without trust::

    export BROWSER_START_AUTH_ENDPOINT_URL="https://pouta.csc.fi:5001/v3"

Setting up TLS termination proxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The backend can be run in secure mode, i.e. with HTTPS enabled, but for
scaling up a TLS termination proxy is recommended. Setting up TLS termination
is outside the scope of this documentation, but a few useful links are
provided along with the necessary configs regarding this service. [#]_ [#]_

Scaling up the service
----------------------
The service runs in a single-threaded mode, since the library that's used for
providing the back-end isn't multi-threaded. Therefore to completely use up a
server’s resources a multi-processed approach must be chosen. The easiest way
to do this is to set up a reverse proxy, which can be run in the same server
that acts as the TLS endpoint.

The aiohttp documentation already gives us directions for the set-up [#]_ so
they won’t be provided here. In its current state the project should be
configured to use TCP sockets in NGINX, so they’re the directions to use in
the aforementioned link. Also change the server run command to enable running
the project as follows::

    command=swift-browser-ui start --port=808%(process_num)s

Further reading and citations
-----------------------------
.. [#] https://click.palletsprojects.com/en/7.x/options/#values-from-environment-variables
.. [#] https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
.. [#] https://docs.nginx.com/nginx/admin-guide/security-controls/terminating-ssl-http/
.. [#] http://docs.aiohttp.org/en/stable/deployment.html
