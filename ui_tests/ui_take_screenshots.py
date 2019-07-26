"""Module for automating the screenshots for the UI documentation."""


import subprocess  # nosec
import time
import os
import sys


from selenium import webdriver


from .common import get_nav_to_ui
from .common import navigate_to_container_with_objects
from .common import wait_for_clickable


class ObjBrowserScreenshot():
    """Base class to inherit when creating an object browser screenshot."""

    def __init__(self):
        """."""
        self.server_process = None
        self.options = None
        self.img_dir = (__file__.split('s3-object-browser')[0] +
                        's3-object-browser/docs/source/_static/images/')
        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)
        self.drv = None

    def raise_server(self):
        """Raise the test server."""
        os.environ['TEST_MAX_OBJECT_SIZE'] = "4294967296"
        self.options = webdriver.firefox.options.Options()
        self.options.headless = True
        self.server_process = subprocess.Popen(  # nosec
            ['python', '-m', 'tests.mock_server'],
            stdout=subprocess.PIPE,
        )
        self.drv = webdriver.Firefox(
            options=self.options
        )
        self.drv.set_window_size(1920, 1080)
        time.sleep(5.0)

    def tear_server(self):
        """Kill the test server."""
        self.drv.quit()
        self.server_process.kill()
        self.server_process.wait()


class TakeScreenshots(ObjBrowserScreenshot):
    """Take screenshots for object browser documentation."""

    def screenshot_login_page(self):
        """Take screenshot of the development login page."""
        self.drv.get('http://localhost:8080')
        time.sleep(0.25)
        with open(self.img_dir + 'screenshot-login-page', 'wb') as img_f:
            img_f.write(self.drv.get_screenshot_as_png())

    def screenshot_front_page(self):
        """Take screenshot of the front page."""
        get_nav_to_ui(self.drv)
        time.sleep(0.25)
        with open(self.img_dir + 'screenshot-front-page', 'wb') as img_f:
            img_f.write(self.drv.get_screenshot_as_png())

    def screenshot_dashboard(self):
        """Take screenshot of the dashboard."""
        get_nav_to_ui(self.drv)
        wait_for_clickable(
            self.drv.find_element_by_link_text("User information")
        )
        time.sleep(0.25)
        with open(self.img_dir + 'screenshot-dashboard', 'wb') as img_f:
            img_f.write(self.drv.get_screenshot_as_png())

    def screenshot_object_page(self):
        """Take screenshot of the object page."""
        get_nav_to_ui(self.drv)
        navigate_to_container_with_objects(self.drv)
        time.sleep(0.25)
        with open(self.img_dir + 'screenshot-object-page', 'wb') as img_f:
            img_f.write(self.drv.get_screenshot_as_png())

    def screenshot_object_details(self):
        """Take screenshot with object details open."""
        get_nav_to_ui(self.drv)
        navigate_to_container_with_objects(self.drv)
        time.sleep(0.25)
        wait_for_clickable(
            self.drv.find_element_by_class_name("chevron-cell")
        )
        time.sleep(0.1)
        with open(self.img_dir + 'screenshot-object-details', 'wb') as img_f:
            img_f.write(self.drv.get_screenshot_as_png())


def run_screenshots(screenshots):
    """Run the screenshots in a list."""
    for screenshot in screenshots:
        try:
            screenshot.raise_server()
            for fun in filter(lambda i: "screenshot_" in i, dir(screenshot)):
                getattr(screenshot, fun)()
        finally:
            screenshot.tear_server()


def main():
    """Execute the screenshots as a main program."""
    try:
        run_screenshots([TakeScreenshots()])
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
