"""Session tests for the object browser with Firefox."""


import time
import random
import os

import pytest
import selenium.webdriver

from .common import ServerThread
from .common import login
from .common import get_cacheless_profile
from .common import wait_for_clickable


random.seed(os.urandom(128))


@pytest.mark.timeout(60)
def test_firefox_session_end_button():
    """Test session logout with the logout button."""
    with ServerThread():
        try:
            opts = selenium.webdriver.firefox.options.Options()
            if os.environ.get("TEST_ENABLE_HEADLESS", None):
                opts.headless = True
            drv = selenium.webdriver.Firefox(
                options=opts,
                firefox_profile=get_cacheless_profile()
            )
            drv.set_window_size(1920, 1080)
            drv.get("http://localhost:8080")
            login(drv)
            time.sleep(0.33)
            wait_for_clickable(
                drv.find_element_by_link_text("Log Out")
            )
            time.sleep(3.00)
            drv.execute_script("location.reload(true);")
            time.sleep(0.5)
            assert (  # nosec
                "Log In" in drv.page_source or
                "Kirjaudu sisään" in drv.page_source
            )
        finally:
            drv.quit()


@pytest.mark.timeout(60)
def test_firefox_session_separation_logouts():
    """Test that session logouts stay separate."""
    with ServerThread():
        try:
            opts = selenium.webdriver.firefox.options.Options()
            if os.environ.get("TEST_ENABLE_HEADLESS"):
                opts.headless = True
            # Create three separate sessions (should be enough to test with),
            # this time leaving the caching on.
            drv_list = [selenium.webdriver.Firefox(
                options=opts,
                firefox_profile=selenium.webdriver.FirefoxProfile()
            ) for i in range(0, 3)]

            # Navigate to the server and log every instance in
            for drv in drv_list:
                drv.set_window_size(1920, 1080)
                drv.get("http://localhost:8080")
                login(drv)

            time.sleep(0.25)
            # Test session logout separation by killing one of the sessions
            to_kill = random.choice(drv_list)  # nosec
            wait_for_clickable(
                to_kill.find_element_by_link_text("Log Out")
            )
            time.sleep(0.25)
            to_kill.quit()
            drv_list.remove(to_kill)
            time.sleep(3.00)

            for drv in drv_list:
                drv.refresh()
            time.sleep(0.25)

            # Check that none of the pages were logged out
            for drv in drv_list:
                assert (  # nosec
                    "Log In" not in drv.page_source and
                    "Kirjaudu sisään" not in drv.page_source
                )

            # After this we can test that the session border doesn't break,
            # i.e. the two remaining sessions have different content.
            for drv in drv_list:
                drv.refresh()
            assert drv_list[0].page_source != drv_list[1].page_source  # nosec
        finally:
            for drv in drv_list:
                drv.quit()
