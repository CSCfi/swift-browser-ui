"""Common functions and variables for the UI tests."""


import subprocess  # nosec
import signal
import time
from contextlib import AbstractContextManager


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException


CLICK_TIMEOUT = 5


def wait_for_clickable(element):
    """Click an element when it's ready."""
# Get the starting time for timing out if the page is actually hanging
    s_time = time.time()
    while time.time() - s_time < CLICK_TIMEOUT:
        try:
            element.click()
            return
        # If the other content hasn't loaded yet
        except ElementClickInterceptedException:
            time.sleep(0.05)
        except WebDriverException as exc:
            if "not clickable" in exc.msg:
                time.sleep(0.05)
            else:
                raise WebDriverException(
                    msg=exc.msg,
                    screen=exc.screen,
                    stacktrace=exc.stacktrace
                )
    raise NoSuchElementException()


def check_download(drv):
    """Check if the download link works."""
    try:
        wait_for_clickable(
            drv.find_element_by_link_text("Download")
        )
    except NoSuchElementException:
        wait_for_clickable(
            drv.find_element_by_link_text("Lataa")
        )
    time.sleep(0.2)
    drv.switch_to.window(drv.window_handles[1])
    time.sleep(0.1)
    if (
            "http://localhost:8443/swift/v1/AUTH_example"
            in drv.current_url and
            "temp_url_expires" in drv.current_url and
            "temp_url_sig" in drv.current_url
    ):
        time.sleep(0.1)
        drv.switch_to.window(drv.window_handles[0])
        return True
    time.sleep(0.1)
    drv.switch_to.window(drv.window_handles[0])
    return False


def check_contents(drv):
    """Check if the open object view contains objects."""
    # Need to sleep for a moment since the loading screen is displayed for a
    # moment before the contents are loaded
    time.sleep(0.15)
    if "This container" not in drv.page_source:
        return drv
    drv.back()
    drv.find_element_by_tag_name("table").send_keys(Keys.ARROW_DOWN)
    drv.find_element_by_tag_name("table").send_keys(Keys.ENTER)
    return check_contents(drv)


def navigate_to_next_full_after_back(drv):
    """Navigate to a container after getting back from another one."""
    drv.find_element_by_tag_name("table").send_keys(Keys.ARROW_DOWN)
    drv.find_element_by_tag_name("table").send_keys(Keys.ENTER)
    check_contents(drv)


def navigate_to_container_with_objects(drv):
    """Navigate to a container that has some objects in it."""
    # Navigate to the first container and check if there's content in it.
    (
        webdriver.common.action_chains.ActionChains(drv)
        .send_keys(Keys.TAB)  # Switching to the table requires 8 tabs, this
        .send_keys(Keys.TAB)  # nicely tets the accessibility as well
        .send_keys(Keys.TAB)
        .send_keys(Keys.TAB)
        .send_keys(Keys.TAB)
        .send_keys(Keys.TAB)
        .send_keys(Keys.TAB)
        .send_keys(Keys.TAB)
        .send_keys(Keys.ARROW_DOWN)  # Get the first container in active table
        .send_keys(Keys.ENTER)  # Hit enter to open container
        .perform()  # Flush the queue into the window
    )
    return check_contents(drv)


def navigate_to_next_container_from_search(drv):
    """Navigate to the next container."""
    (
        webdriver.common.action_chains.ActionChains(drv)
        .send_keys(Keys.TAB)
        .send_keys(Keys.ARROW_DOWN)
        .send_keys(Keys.ENTER)
        .perform()
    )


def switch_to_finnish(drv):
    """Change localization to Finnish."""
    s_time = time.time()
    while time.time() - s_time < CLICK_TIMEOUT:
        try:
            webdriver.support.ui.Select(
                drv.find_element_by_tag_name("select")
            ).select_by_index(1)
            return
        except ElementClickInterceptedException:
            time.sleep(0.1)
        except WebDriverException as exc:
            if "not clickable" in exc.msg:
                time.sleep(0.05)
            else:
                raise WebDriverException(
                    msg=exc.msg,
                    screen=exc.screen,
                    stacktrace=exc.stacktrace
                )
    raise NoSuchElementException()


def get_nav_to_ui(drv):
    """Navigate to the browser UI."""
    drv.get("http://localhost:8080")
    login(drv)
    time.sleep(0.1)
    return drv


def get_nav_out(drv):
    """End the browser session."""
    time.sleep(0.1)
    try:
        wait_for_clickable(
            drv.find_element_by_link_text("Log Out")
        )
    except NoSuchElementException:
        wait_for_clickable(
            drv.find_element_by_link_text("Kirjaudu ulos")
        )
    finally:
        time.sleep(0.1)
        drv.refresh()
        drv.quit()


def login(drv):
    """Log in the user in a specific selenium driver instance."""
    drv.find_element_by_id("inputbox").submit()
    while drv.current_url != \
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


# The server needs to run in a separate thread, and that's easiest to do when
# running it in a separate process. Thus, a context manager to spin up the
# test server instance before the tests, and killing the process afterwards
# to free up the port.
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
        # time.sleep(3)  # a quick sleep to let the server catch on

    def __exit__(self, exc_type, exc_value, traceback):
        """."""
        # Kill the server on exit.
        self.server_thread.send_signal(signal.SIGINT)
