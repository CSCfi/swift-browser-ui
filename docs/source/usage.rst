Getting started
===============

.. note::
    Please note that the things related to project development aren’t
    documented here, and everything on this page is only related to the
    running of the program

After the setup has been completed as illustrated in :ref:`setup` the
server can be used with the ``s3browser`` command, the command line options
can be found below.


Command line interface
----------------------

The project has a command line interface, that can be used to quickly test the
frontend for different endpoints and usage cases. It provides basic
functionality e.g. starting the server and specify a variety of different
settings, detailed below:

.. code-block:: console

    ➜ s3browser --help
    Usage: s3browser [OPTIONS] COMMAND [ARGS]...

    Command line interface for managing s3browser.

    Options:
    --version       Show the version and exit.
    -v, --verbose   Increase program verbosity.
    -D, --debug     Enable debug level logging.
    --logfile TEXT  Write program logs to a file.
    --help          Show this message and exit.

    Commands:
    start    Start the browser backend and server.


Global arguments
~~~~~~~~~~~~~~~~
The following command line arguments affect all of the commands in the
application:

--verbose                      Flag to increase program verbosity.
--debug                        Enable program debug messages.
--logfile FILE                 Save all program output to a file.
--help                         Help on the CLI usage.
--version                      Display the program version


The server startup
~~~~~~~~~~~~~~~~~~

The following command line arguments are available for server startup.

.. code-block:: console

    ➜ s3browser start --help
    Usage: s3browser start [OPTIONS]

    Start the browser backend and server.

    Options:
    -p, --port INTEGER         Set the port the server is run on.
    --auth-endpoint-url TEXT   Endpoint for the Openstack keystone API in use.
    --has-trust                Flag if the program is listed on the
                               trusted_dashboards in the specified address.
    --set-origin-address TEXT  Set the address that the program will be
                               redirected to from WebSSO
    --help                     Show this message and exit.


--port PORT                    Set the port that the server will use.
--auth-endpoint-url URL        REQUIRED – Set the endpoint that the program
                               uses for authentication. The program cannot
                               work without this.
--set-origin-address TEXT      Set the address that the program will be redirected
                               to from WebSSO.
--has-trust                    Toggle if the program has trust on the specified
                               authentication endpoint, i.e. if the program has
                               been listed on the respective Openstack keystone
                               trusted_dashboard list. [#]_

.. [#] https://docs.openstack.org/keystone/pike/advanced-topics/federation/websso.html
