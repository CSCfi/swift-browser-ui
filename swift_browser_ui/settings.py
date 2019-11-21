"""
Module containing all of the settings required in the global scope.

The different configurations are also listed here:

.. code-block::

    auth_endpoint_url:  The correct address for the relevant Openstack keystone
                        instance, to enable the authentication backend
                        Default: None
    has_trust:          Information on whether or not the backend has trust on
                        the specified endpoint, i.e. if the backend can use SSO
                        Default: False
    swift_endpoint_url: The endpoint which the backend will use for OS Swift,
                        to query the object storage.
                        Default: None
    logfile:            The file in which the logs will be written into, if the
                        logfile is set.
                        Default: None
    port:               The port in which the server will answer from (this
                        option is only relevant if the server is run in a
                        standalone setup)
                        Default: 8080
    verbose:            Boolean value for increasing verbosity in the program
                        Default: False
    debug:              Set logging level to debug
                        Default: False
    version:            Contains the current version for e.g. logging
    static_folder:      Path to the folder that contains the static front-end
                        files, only used when the server is deployed without
                        a proxy like Nginx to host the static files, and handle
                        load balancing
                        Default: $PWD/swift_browser_ui_frontend

"""


import logging
from os import environ


FORMAT = """\
[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] \
(L:%(lineno)s) %(funcName)s: %(message)s\
"""
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

# Log from envvar as well, since the CLI shouldn't be the only option.
# Semantics are identical with the frontend, so i.e.:
# BROWSER_VERBOSE (LOGLEVEL INFO), BROWSER_DEBUG (LOGLEVEL DEBUG)
if environ.get('BROWSER_VERBOSE', None):
    logging.root.setLevel(logging.INFO)
if environ.get('BROWSER_DEBUG', None):
    logging.root.setLevel(logging.DEBUG)

# The following is the variable containing the default settings, which will be
# overloaded as necessary.
setd = {
    "auth_endpoint_url": environ.get(
        "BROWSER_START_AUTH_ENDPOINT_URL",
        environ.get(
            "OS_AUTH_URL", None
        )),
    "sharing_endpoint": environ.get(
        "BROWSER_START_SHARING_ENDPOINT_URL", None
    ),
    "request_endpoint": environ.get(
        "BROWSER_START_REQUEST_ENDPOINT_URL", None
    ),
    "sharing_request_token": environ.get(
        "SWIFT_UI_SHARING_REQUEST_TOKEN", None
    ).encode("utf-8"),
    "has_trust": False,
    "logfile": None,
    "port": 8080,
    "verbose": False,
    "debug": False,
    "version": None,
    "set_session_devmode": False,
    "static_directory": __file__.replace("/settings.py", "") + "/static"
}


def set_key(key, value, log_message):
    """Set a key value if it's specified."""
    if value:
        logging.info(log_message, str(value))
        setd[key] = value
