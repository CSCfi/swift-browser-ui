"""Session tests for the object browser."""


import time
import random
import os

import selenium.webdriver

from .common import ServerThread
from .common import login
from .common import get_cacheless_profile


random.seed(os.urandom(128))


def test_session_end_button():
    """Test session logout with the logout button."""
    with ServerThread():
        try:
            drv = selenium.webdriver.Firefox(
                firefox_profile=get_cacheless_profile()
            )
            drv.get("http://localhost:8080")
            login(drv)
            time.sleep(0.33)
            logout_el = drv.find_element_by_link_text("Log Out")
            logout_el.click()
            time.sleep(0.33)
            drv.execute_script("location.reload(true);")
            time.sleep(0.5)
            assert "Unauthorized" in drv.page_source  # nosec
        finally:
            drv.quit()


def test_session_end_page_leave():
    """Test session logout upon the page leave."""
    with ServerThread():
        try:
            drv = selenium.webdriver.Firefox(
                firefox_profile=get_cacheless_profile()
            )
            drv.get("http://localhost:8080")
            login(drv)
            old_session = drv.current_url
            drv.get("http://localhost:8080")
            time.sleep(0.5)
            drv.get(old_session)
            time.sleep(0.33)
            assert "Unauthorized" in drv.page_source  # nosec
        finally:
            drv.quit()


def test_session_separation_logouts():
    """Test that session logouts stay separate."""
    with ServerThread():
        try:
            # Create three separate sessions (should be enough to test with),
            # this time leaving the caching on.
            drv_list = [selenium.webdriver.Firefox(
                firefox_profile=selenium.webdriver.FirefoxProfile()
            ) for i in range(0, 3)]

            # Navigate to the server and log every instance in
            for drv in drv_list:
                drv.get("http://localhost:8080")
                login(drv)

            # Test session logout separation by killing one of the sessions
            to_kill = random.choice(drv_list)  # nosec
            to_kill_logout = to_kill.find_element_by_link_text("Log Out")
            to_kill_logout.click()
            time.sleep(0.25)
            to_kill.quit()
            drv_list.remove(to_kill)

            for drv in drv_list:
                drv.refresh()
            time.sleep(0.25)

            # Check that none of the pages were logged out
            for drv in drv_list:
                assert "Unauthorized" not in drv.page_source  # nosec

            # After this we can test that the session border doesn't break,
            # i.e. the two remaining sessions have different content.
            for drv in drv_list:
                drv.refresh()
            assert drv_list[0].page_source != drv_list[1].page_source  # nosec
        finally:
            for drv in drv_list:
                drv.quit()
