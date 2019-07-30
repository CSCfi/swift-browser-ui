"""Module for creating a server with mock-up openstack."""


from os import environ
import unittest.mock
import logging


import s3browser.server


# Import some mock-ups that are already made before
from .mockups import return_project_avail
from .mockups import Mock_Service, Mock_Session


SESSION_MODE = bool(environ.get("TEST_SESSION_MODE", False))


logging.basicConfig()
logging.root.setLevel(logging.DEBUG)


def mock_initiate_os_session(token, _):
    """Create a mock os session object."""
    return Mock_Session()


def mock_initiate_swift_service(_):
    """Create a mock os swift service object."""
    serv = Mock_Service()
    serv.init_with_data(
        # Default container amount is 10, can be overriden with envvar.
        containers=int(environ.get("TEST_CONTAINER_AMOUNT", 10)),
        # Default object range is [0, 25[, the max can be overridden
        # with envvar.
        object_range=(
            0,
            int(environ.get("TEST_MAX_OBJECT_AMOUNT", 25)),
        ),
        # Default size range is [0, 1048576[, the max can be overridden
        # with envvar.
        size_range=(
            1,
            int(environ.get("TEST_MAX_OBJECT_SIZE", 1048576))
        )
    )
    # The downloads aren't mocked, so no contents to any file. This isn't
    # something we need to test, and also would consume too much resources.
    # NOTE: Some random metadata creation could be added here.
    return serv


async def mock_graceful_shutdown(_):
    """."""


@unittest.mock.patch(
    "s3browser.server.kill_sess_on_shutdown",
    mock_graceful_shutdown
)
@unittest.mock.patch(
    "s3browser.login.initiate_os_session",
    mock_initiate_os_session
)
@unittest.mock.patch(
    "s3browser.login.initiate_os_service",
    mock_initiate_swift_service
)
@unittest.mock.patch(
    "s3browser.login.get_availability_from_token",
    return_project_avail
)
@unittest.mock.patch.dict(
    s3browser.server.setd,
    {
        "auth_endpoint_url": "https://localhost:5001/v3",
        "has_trust": False,
        "logfile": None,
        "port": 8080,
        "verbose": True,
        "debug": True,
        "set_session_devmode": SESSION_MODE,
        "static_directory":
        s3browser.settings.__file__.replace("/settings.py", "") + "/static"
    }
)
def run_mock_server():
    """Run test server with mock openstack."""
    # Run the server in an ordinary fashion after patching everything
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    app = s3browser.server.servinit()
    s3browser.server.run_server_insecure(app)


if __name__ == '__main__':
    run_mock_server()
