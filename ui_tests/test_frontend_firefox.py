"""Front-end tests for the object browser, firefox."""


import time


import pytest


from .common_with_unittests import FirefoxTestClass
from .common import navigate_to_container_with_objects
from .common import check_download
from .common import switch_to_finnish
from .common import navigate_to_next_container_from_search
from .common import navigate_to_next_full_after_back
from .common import wait_for_clickable


class TestFirefoxFrontend(FirefoxTestClass):
    """Test the frontend wiht firefox."""

    @pytest.mark.timeout(60)
    def test_download_from_random_bucket(self):
        """Test if file download link works and can be used."""
        self.drv = navigate_to_container_with_objects(self.drv)
        time.sleep(0.25)
        self.assertTrue(check_download(self.drv))

    @pytest.mark.timeout(60)
    def test_download_from_random_bucket_fin(self):
        """Testif the previous file download test works with fi locale."""
        switch_to_finnish(self.drv)
        self.drv = navigate_to_container_with_objects(self.drv)
        time.sleep(0.25)
        self.assertTrue(check_download(self.drv))

    @pytest.mark.timeout(60)
    def test_find_file_checksums(self):
        """Test seeking file checksums from the table listing."""
        self.drv = navigate_to_container_with_objects(self.drv)
        time.sleep(0.25)
        # The following finds the first table row with a detail container, and
        # clicks said container open.
        wait_for_clickable(
            self.drv.find_element_by_class_name("chevron-cell")
        )
        element = (
            self.drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        # Check that the checksum is present.
        self.assertIn("Hash", element.text)

    @pytest.mark.timeout(60)
    def test_find_file_checksums_fin(self):
        """Test seeking file checksums with finnish local."""
        # Again firefox needs a bit more waiting around to prevent web driver
        # from crashing (implicit wait would work otherwise, but the problem
        # is that the element is present, it's just obstructed)
        time.sleep(0.1)
        switch_to_finnish(self.drv)
        time.sleep(0.25)
        self.drv = navigate_to_container_with_objects(self.drv)
        time.sleep(0.2)
        wait_for_clickable(
            self.drv.find_element_by_class_name("chevron-cell")
        )
        element = (
            self.drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        self.assertIn("Tarkistussumma", element.text)

    @pytest.mark.timeout(60)
    def test_search_a_container(self):
        """Test searching a specific container and navigating to it."""
        # The search box is the only input type form on the page.
        self.drv.find_element_by_class_name("input").send_keys(
            "test-container-3"
        )
        time.sleep(0.25)
        navigate_to_next_container_from_search(self.drv)
        time.sleep(0.25)
        self.assertIn("test-container-3", self.drv.current_url)
        time.sleep(0.2)

    @pytest.mark.timeout(60)
    def test_long_user_session(self):
        """Test the UI for a longer session."""
        # Perform a container search
        time.sleep(0.1)
        self.drv.find_element_by_class_name("input").send_keys(
            "test-container-4"
        )
        time.sleep(0.25)
        navigate_to_next_container_from_search(self.drv)
        self.assertIn("test-container-4", self.drv.current_url)
        # Go back and check the next container with some objects inside.
        time.sleep(0.1)
        self.drv.back()
        time.sleep(0.1)
        navigate_to_next_full_after_back(self.drv)
        # Test downloading the first object from the newly open container.
        time.sleep(0.25)
        self.assertTrue(check_download(self.drv))
        time.sleep(0.1)
        self.drv.back()
        time.sleep(0.1)
        # Switch to finnish and test navigating to the user page.
        switch_to_finnish(self.drv)
        time.sleep(0.25)
        wait_for_clickable(
            self.drv.find_element_by_link_text("test_user_id")
        )
        time.sleep(0.1)
        # NOTE: replace this with a proper assertion when the dashboard is
        # implemented
        self.assertIn("Käyttäjä", self.drv.page_source)
        self.assertIn("Kontteja", self.drv.page_source)
        self.assertIn("Objekteja", self.drv.page_source)
        self.assertIn("Tilankäyttö", self.drv.page_source)
        self.drv.back()
        time.sleep(0.1)
        # Perform one hash check still, in Finnish.
        navigate_to_next_full_after_back(self.drv)
        time.sleep(0.25)
        wait_for_clickable(
            self.drv.find_element_by_class_name("chevron-cell")
        )
        element = (
            self.drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        self.assertIn("Tarkistussumma", element.text)
