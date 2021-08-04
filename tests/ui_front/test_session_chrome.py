"""Session tests for the object browser with Chrome."""

import time
import random
from os import environ, urandom

import pytest
from selenium import webdriver

from .common_with_unittests import BaseUITestClass
from .common import get_nav_to_ui
from .common import wait_for_clickable


random.seed(urandom(128))


class TestChromeSession(BaseUITestClass):
    """Test the sessions wiht chrome."""

    def setUp(self):
        """Set up options for Chrome driver."""
        super().setUp()
        self.opts = webdriver.chrome.options.Options()
        if environ.get("TEST_ENABLE_HEADLESS", None):
            self.opts.headless = True
            self.opts.add_argument("--no-sandbox")
            self.opts.add_argument("--disable-dev-shm-usage")

    def tearDown(self):
        """Terminate mock web server process."""
        super().tearDown()

    @pytest.mark.timeout(60)
    def test_chrome_session_end_button(self):
        """Test session logout with the logout button."""
        drv = webdriver.Chrome(options=self.opts)
        drv.set_window_size(1920, 1080)
        get_nav_to_ui(drv)
        wait_for_clickable(drv.find_element_by_link_text("Log Out"))
        time.sleep(0.5)
        self.assertTrue(
            "Log In" in drv.page_source or "Kirjaudu sisään" in drv.page_source
        )
        drv.quit()

    @pytest.mark.timeout(60)
    def test_chrome_session_separation_logouts(self):
        """Test that session logouts stay separate."""
        # Create three separate sessions (should be enough to test with),
        # this time leaving the caching on.
        drv_list = [webdriver.Chrome(options=self.opts) for i in range(0, 3)]

        # Navigate to the server and log every instance in
        for drv in drv_list:
            drv.set_window_size(1920, 1080)
            get_nav_to_ui(drv)

        # Test session logout separation by killing one of the sessions
        to_kill = random.choice(drv_list)  # nosec
        wait_for_clickable(to_kill.find_element_by_link_text("Log Out"))
        time.sleep(0.25)
        to_kill.quit()
        drv_list.remove(to_kill)
        time.sleep(3.00)

        for drv in drv_list:
            drv.refresh()
        time.sleep(0.25)

        # Check that none of the pages were logged out
        for drv in drv_list:
            self.assertTrue(
                "Log In" not in drv.page_source
                or "Kirjaudu sisään" not in drv.page_source
            )

        # After this we can test that the session border doesn't break,
        # i.e. the two remaining sessions have different content.
        for drv in drv_list:
            drv.refresh()
        self.assertNotEqual(drv_list[0].page_source, drv_list[1].page_source)
        for drv in drv_list:
            drv.quit()
