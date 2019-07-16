"""Common functions and variables for the UI tests."""


import subprocess  # nosec
import signal
import time


from contextlib import AbstractContextManager


def login(driver_instance):
    """Log in the user in a specific selenium driver instance."""
    el = driver_instance.find_element_by_id("inputbox")
    el.submit()
    while driver_instance.current_url != \
            "http://localhost:8080/browse/test_user_id/placeholder":
        time.sleep(0.25)


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
