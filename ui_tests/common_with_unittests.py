"""Common functions implemented as unittests inherited classes."""


import unittest
import subprocess  # nosec
import time
from os import environ


from selenium import webdriver


from .common import get_nav_out, get_nav_to_ui


class BaseUITestClass(unittest.TestCase):
    """Base class for the browsers with server init and teardown."""

    def setUp(self):
        """."""
        self.server_process = subprocess.Popen(  # nosec
            [
                "python",
                "-m",
                "tests.mock_server"
            ],
            stdout=subprocess.PIPE
        )
        time.sleep(3.0)

    def tearDown(self):
        """."""
        self.server_process.kill()
        self.server_process.wait()


class FirefoxTestClass(BaseUITestClass):
    """Class for testing with Firefox."""

    def setUp(self):
        """."""
        super().setUp()
        self.opts = webdriver.firefox.options.Options()
        if environ.get("TEST_ENABLE_HEADLESS", None):
            self.opts.headless = True
        self.drv = webdriver.Firefox(options=self.opts)
        self.drv.set_window_size(1920, 1080)
        get_nav_to_ui(self.drv)

    def tearDown(self):
        """."""
        get_nav_out(self.drv)


class ChromiumTestClass(BaseUITestClass):
    """Class for testing with Chromium."""

    def setUp(self):
        """."""
        super().setUp()
        self.opts = webdriver.chrome.options.Options()
        if environ.get("TEST_ENABLE_HEADLESS", None):
            self.opts.headless = True
            self.opts.add_argument('--no-sandbox')
            self.opts.add_argument('--disable-dev-shm-usage')
        self.drv = webdriver.Chrome(options=self.opts)
        self.drv.set_window_size(1920, 1080)
        get_nav_to_ui(self.drv)

    def tearDown(self):
        """."""
        get_nav_out(self.drv)
