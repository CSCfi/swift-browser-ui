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
functionality e.g. starting the server and specify a variety of 
different settings, detailed below:

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
    install  Install the browser backend (implemented in the future).
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

.. [#] https://docs.openstack.org/keystone/pike/advanced-topics/federation/websso.html
