"""Common functions and variables for the UI tests."""


import time
import os


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException


CLICK_TIMEOUT = 5
ADDRESS = "http://localhost:" + str(os.environ.get("TEST_SERVER_PORT", 8080))


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
    time.sleep(0.3)
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


def check_contents(drv, arrows=1):
    """Check if the open object view contains objects."""
    # Need to sleep for a moment since the loading screen is displayed for a
    # moment before the contents are loaded
    time.sleep(0.15)
    if ("This container" not in drv.page_source and
            "Säiliö on" not in drv.page_source):
        return drv
    drv.back()
    for _ in range(0, arrows):
        drv.find_element_by_tag_name("table").send_keys(Keys.ARROW_DOWN)
    drv.find_element_by_tag_name("table").send_keys(Keys.ENTER)
    return check_contents(drv, arrows=arrows + 1)


def navigate_to_next_full_after_back(drv):
    """Navigate to a container after getting back from another one."""
    drv.find_element_by_tag_name("table").send_keys(Keys.ARROW_DOWN)
    drv.find_element_by_tag_name("table").send_keys(Keys.ENTER)
    check_contents(drv)


def navigate_to_container_with_objects(drv):
    """Navigate to a container that has some objects in it."""
    # Navigate to the first container and check if there's content in it.
    drv.find_element_by_tag_name("table").send_keys(Keys.ARROW_DOWN)
    drv.find_element_by_tag_name("table").send_keys(Keys.ENTER)
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


def get_nav_to_ui(drv, address=ADDRESS):
    """Navigate to the browser UI."""
    drv.get(address)
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
        time.sleep(0.25)
        drv.refresh()
        drv.quit()


def login(drv):
    """Log in the user in a specific selenium driver instance."""
    try:
        wait_for_clickable(
            drv.find_element_by_link_text("Log In")
        )
    except NoSuchElementException:
        wait_for_clickable(
            drv.find_element_by_link_text("Kirjaudu sisään")
        )
    drv.implicitly_wait(1)

    login_field = drv.find_element_by_id("inputbox")
    login_field.send_keys("abcdefabcdefabcdefabcdefabcdefab")
    login_field.submit()
    while drv.current_url != \
            ADDRESS + "/browse/test_user_id/placeholder":
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
