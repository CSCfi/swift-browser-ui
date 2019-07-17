"""Common functions and variables for the UI tests."""


import subprocess  # nosec
import signal
import time
from contextlib import AbstractContextManager


from selenium.webdriver import FirefoxProfile


def login(driver_instance):
    """Log in the user in a specific selenium driver instance."""
    el = driver_instance.find_element_by_id("inputbox")
    el.submit()
    while driver_instance.current_url != \
            "http://localhost:8080/browse/test_user_id/placeholder":
        time.sleep(0.25)


def get_cacheless_profile():
    """Create a cacheless profile for Firefox webdriver."""
    ret = FirefoxProfile()
    ret.set_preference(
        "browser.cache.memory.enable", False
    )
    ret.set_preference(
        "browser.cache.disk.enable", False
    )
    return ret


class ServerThread(AbstractContextManager):
    """Context manager for the test server."""

    def __init__(self):
        """."""
        self.server_thread = None

    def __enter__(self):
        """."""
        self.server_thread = subprocess.Popen(  # nosec
            [
                "python",
                "-m",
                "tests.mock_server"
            ],
            stdout=subprocess.PIPE
        )
        time.sleep(3)

    def __exit__(self, exc_type, exc_value, traceback):
        """."""
        # Kill the server on exit.
        self.server_thread.send_signal(signal.SIGINT)
