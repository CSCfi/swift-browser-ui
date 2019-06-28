"""
A module containing all of the settings required in a complete global scope,
e.g. logging filenames, API endpoints, logging levels etc.

The different configs are listed in the defaults.conf, but also here in the
docstring (the more locations, the better).

auth_endpoint_url:     The correct address for the relevant Openstack keystone
                       instance, to enable the authentication backend
                       Default: None
has_trust:             Information on whether or not the backend has trust on
                       the specified endpoint, i.e. if the backend can use SSO
                       Default: False
swift_endpoint_url:    The endpoint which the backend will use for OS Swift,
                       to query the object storage.
                       Default: None
logfile:               The file in which the logs will be written into, if the
                       logfile is set.
                       Default: None
port:                  The port in which the server will answer from (this
                       option is only relevant if the server is run in a
                       standalone setup)
                       Default: 8080
verbose:               Boolean value for increasing verbosity in the program
                       Default: False
debug:                 Set logging level to debug
                       Default: False
version:               Contains the current version for e.g. logging
static_folder:         Path to the folder that contains the static front-end
                       files, only used when the server is deployed without
                       a proxy like Nginx to host the static files, and handle
                       load balancing
                       Default: $PWD/s3browser_frontend
"""


import logging


# The following is the variable containing the default settings, which will be
# overloaded as necessary.
setd = {
    "auth_endpoint_url": None,
    "has_trust": False,
    "swift_endpoint_url": None,
    "logfile": None,
    "port": 8080,
    "verbose": False,
    "debug": False,
    "version": None,
    "static_directory": None,
}


def set_key(key, value, log_message):
    global setd
    if value:
        logging.info(log_message + str(value))
        setd[key] = value
