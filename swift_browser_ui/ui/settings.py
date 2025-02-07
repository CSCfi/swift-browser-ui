"""Module containing all of the settings required in the global scope.

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
from typing import Dict, Union

FORMAT = """\
[%(asctime)s][%(name)s][%(process)d %(processName)s][%(levelname)-8s] \
(L:%(lineno)s) %(funcName)s: %(message)s\
"""
logging.basicConfig(format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

# Log from envvar as well, since the CLI shouldn't be the only option.
# Semantics are identical with the frontend, so i.e.:
logging.root.setLevel(environ.get("LOG_LEVEL", "INFO"))

# The following is the variable containing the default settings, which will be
# overloaded as necessary.
setd: Dict[str, Union[str, int, bool, None]] = {
    "auth_endpoint_url": environ.get(
        "BROWSER_START_AUTH_ENDPOINT_URL", environ.get("OS_AUTH_URL", "")
    ),
    "keystone_oidc_provider": environ.get("BROWSER_START_KEYSTONE_OIDC_PROVIDER", "oidc"),
    "sharing_endpoint": environ.get("BROWSER_START_SHARING_ENDPOINT_URL", None),
    "sharing_internal_endpoint": environ.get(
        "BROWSER_START_SHARING_INT_ENDPOINT_URL", None
    ),
    "request_endpoint": environ.get("BROWSER_START_REQUEST_ENDPOINT_URL", None),
    "request_internal_endpoint": environ.get(
        "BROWSER_START_REQUEST_INT_ENDPOINT_URL", None
    ),
    "upload_internal_endpoint": environ.get("BROWSER_START_RUNNER_ENDPOINT", None),
    "upload_external_endpoint": environ.get("BROWSER_START_RUNNER_EXT_ENDPOINT", None),
    "sharing_request_token": environ.get("SWIFT_UI_SHARING_REQUEST_TOKEN", None),
    "has_trust": environ.get("BROWSER_START_HAS_TRUST", False),
    "set_origin_address": environ.get("BROWSER_START_SET_ORIGIN_ADDRESS", None),
    "tempurl_digest_type": environ.get("TEMPURL_USE_DIGEST", "sha1"),
    "os_user_domain": environ.get("OS_USER_DOMAIN_NAME", "Default"),
    "os_accepted_roles": environ.get("OS_ACCEPTED_ROLES", "object_store_user"),
    "force_restricted_mode": environ.get("SWIFT_UI_FORCE_RESTRICTED_MODE", False),
    "logfile": None,
    "port": 8080,
    "verbose": False,
    "debug": False,
    "version": None,
    "set_session_devmode": False,
    "static_directory": __file__.replace("settings.py", "static"),
    "session_lifetime": 28800,
    "history_lifetime": 2592000,
    "oidc_enabled": environ.get("OIDC_ENABLED", "False") == "True",
    "oidc_url": environ.get("OIDC_URL", None),
    "oidc_client_id": environ.get("OIDC_CLIENT_ID", None),
    "oidc_client_secret": environ.get("OIDC_CLIENT_SECRET", None),
    "oidc_redirect_uris": environ.get("OIDC_REDIRECT_URIS", ""),
    "sdconnect_enabled": environ.get("SDCONNECT_ENABLED", "False") == "True",
    "vault_service_id": environ.get("VAULT_SERVICE_ID", "SD-Connect"),
}


def set_key(key: str, value: Union[str, int, None], log_message: str) -> None:
    """Set a key value if it's specified."""
    if value:
        logging.info(log_message, str(value))
        setd[key] = value
