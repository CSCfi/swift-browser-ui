"""Session tests for the object browser."""


import time

import selenium.webdriver

from .common import ServerThread
from .common import login


def get_cachless_profile():
    """Create a cacheless profile for Firefox webdriver."""
    ret = selenium.webdriver.FirefoxProfile()
    ret.set_preference(
        "browser.cache.memory.enable", False
    )
    ret.set_preference(
        "browser.cache.disk.enable", False
    )
    return ret


def test_session_end_button():
    """Test session logout with the logout button."""
    with ServerThread():
        try:
            drv = selenium.webdriver.Firefox(
                firefox_profile=get_cachless_profile()
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
                firefox_profile=get_cachless_profile()
            )
            drv.get("http://localhost:8080")
            login(drv)
            old_session = drv.current_url
            drv.get("http://localhost:8080")
            time.sleep(0.25)
            drv.get(old_session)
            time.sleep(0.25)
            drv.execute_script("location.reload(true);")
            time.sleep(0.5)
            assert "Unauthorized" in drv.page_source  # nosec
        finally:
            drv.quit()
