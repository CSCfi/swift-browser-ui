=====
Usage
=====

.. contents:: Table of Contents
   :depth: 3

Getting started
===============

.. note::
    Please note that the things related to project development aren’t
    documented here, and everything on this page is only related to the
    running of the program

Installation
------------
The program can be installed with pip from the git repository::

    # Requires python >= 3.6
    git clone git@gitlab.csc.fi:CSCCSDP/s3-object-browser.git
    pip install .

When installed the program can be used with the `s3browser` -command, more
complete instructions can be found below.

Command line interface
======================
Description
-----------
The project has a command line interface, that can be used to quickly test the
frontend for different endpoints and usage cases. It has the basic
functionality that you’d expect from a CLI, making it possible to start the
server and specify a variety of different settings.

Global arguments
----------------
The following command line arguments affect all of the commands in the
program:

--verbose                      Flag to increase program verbosity.
--debug                        Enable program debug messages.
--logfile FILE                 Save all program output to a file.
--help                         Help on the CLI usage.
--version                      Display the program version

The server startup
------------------
--port PORT                    Set the port that the server will use.
--static-directory PATH        Set a directory in which the static content of
                               the UI is located. Used mainly for development
                               purposes.
--auth-endpoint-url URL        REQUIRED – Set the endpoint that the program
                               uses for authentication. The program cannot
                               work without this.
--has-trust                    Toggle if the program has trust on the specified
                               authentication endpoint, i.e. if the program has
                               been listed on the respective Openstack keystone
                               trusted_dashboard list. [#]_
--swift-endpoint-url URL       REQUIRED – Set the endpoint that the program
                               uses for object storage. Required for the
                               download functionality to work.

Configuration
=============
Environment variable naming
---------------------------
The command line arguments can also be configured as environment variables,
the environment variable syntax is focumented best in the python click
documentation [#]_ , since that’s what its implemented with. The general
syntax goes as follows::

    BROWSER_$ARGUMENT
    # OR
    BROWSER_$SUBCOMMAND_$ARGUMENT

Example environment variable files
----------------------------------
For the Pouta test environment with NGINX TLS termination proxy in use::

    export BROWSER_START_AUTH_ENDPOINT_URL="https://pouta-test.csc.fi:5001/v3"
    export BROWSER_START_SWIFT_ENDPOINT_URL="https://object.pouta-test.csc.fi:443/swift"
    export BROWSER_START_STATIC_DIRECTORY="s3browser_frontend"
    export BROWSER_START_PORT="8081"
    export BROWSER_START_SET_ORIGIN_ADDRESS="https://vm1950.kaj.pouta.csc.fi:8080/login/websso"

For the Pouta production environment for testing unsecurely without trust::

    export BROWSER_START_AUTH_ENDPOINT_URL="https://pouta.csc.fi:5001/v3"
    export BROWSER_START_SWIFT_ENDPOINT_URL="https://object.pouta.csc.fi:443/swift"
    export BROWSER_START_STATIC_DIRECTORY="s3browser_frontend"

Setting up TLS termination proxy
--------------------------------
The backend itself is not meant to be run as standalone in a production
environment. Therefore in a running config a TLS termination proxy should be
used to make the service secure. Setting up TLS termination is outside the
scope of this documentation, but a few useful links are provided along with
the necessary configs regarding this service. [#]_ [#]_

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

    command=python3 -m s3browser.shell start --port=808%(process_num)s

Further reading and citations
-----------------------------
.. [#] https://docs.openstack.org/keystone/pike/advanced-topics/federation/websso.html
.. [#] https://click.palletsprojects.com/en/7.x/options/#values-from-environment-variables
.. [#] https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
.. [#] https://docs.nginx.com/nginx/admin-guide/security-controls/terminating-ssl-http/
.. [#] http://docs.aiohttp.org/en/stable/deployment.html
