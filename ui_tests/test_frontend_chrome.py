"""Front-end tests for the object browser, chrome."""


import time


import pytest


from .common import handle_chrome_ui_test as handle_ui_test
from .common import navigate_to_container_with_objects
from .common import check_download
from .common import switch_to_finnish
from .common import navigate_to_next_container_from_search
from .common import navigate_to_next_full_after_back


@pytest.mark.timeout(60)
def test_download_from_random_bucket():
    """Test if file download link works and can be navigated to."""
    # Pylint is incorrect on the variable being unused
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_download(drv):
        # Find a container with stuff
        drv = navigate_to_container_with_objects(drv)
        assert check_download(drv)  # nosec


@pytest.mark.timeout(60)
def test_download_from_random_bucket_fin():
    """Test if the previous file download test works with finnish local."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_download(drv):
        switch_to_finnish(drv)
        drv = navigate_to_container_with_objects(drv)
        assert check_download(drv)  # nosec


@pytest.mark.timeout(60)
def test_find_file_chekcsums():
    """Test seeking file checksums from the table listing."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_checksum(drv):
        drv = navigate_to_container_with_objects(drv)
        drv.find_element_by_class_name("chevron-cell").click()
        # The following finds the first table row with a detail container, and
        # clicks said container open.
        el = (
            drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        # Check that the checksum is present.
        assert "Hash" in el.text  # nosec


@pytest.mark.timeout(60)
def test_find_file_checksums_fin():
    """Test seeking file checksums with finnish local."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_checksum_fin(drv):
        switch_to_finnish(drv)
        drv = navigate_to_container_with_objects(drv)
        drv.find_element_by_class_name("chevron-cell").click()
        el = (
            drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        assert "Tarkistussumma" in el.text  # nosec


@pytest.mark.timeout(60)
def test_search_a_container():
    """Test searching a specific container and navigating to it."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_search_bar(drv):
        # The search box is the only input type form on the page.
        drv.find_element_by_class_name("input").send_keys(
            "test-container-3"
        )
        time.sleep(0.25)
        navigate_to_next_container_from_search(drv)
        assert "test-container-3" in drv.current_url  # nosec
        time.sleep(0.1)


@pytest.mark.timeout(60)
def test_long_user_session():
    """Test the UI for a longer session."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_long_session(drv):
        # Perform a container search
        time.sleep(0.1)
        drv.find_element_by_class_name("input").send_keys(
            "test-container-4"
        )
        time.sleep(0.25)
        navigate_to_next_container_from_search(drv)
        assert "test-container-4" in drv.current_url  # nosec
        # Go back and check the next container with some objects inside.
        time.sleep(0.1)
        drv.back()
        time.sleep(0.1)
        navigate_to_next_full_after_back(drv)
        # Test downloading the first object from the newly open container.
        time.sleep(0.25)
        assert check_download(drv)  # nosec
        time.sleep(0.1)
        drv.back()
        time.sleep(0.1)
        # Switch to finnish and test navigating to the user page.
        switch_to_finnish(drv)
        time.sleep(0.1)
        drv.find_element_by_link_text("test_user_id").click()
        time.sleep(0.1)
        # NOTE: replace this with a proper assertion when the dashboard is
        # implemented
        assert "Not yet implemented" in drv.page_source  # nosec
        drv.back()
        time.sleep(0.1)
        # Perform one hash check still, in Finnish.
        navigate_to_next_full_after_back(drv)
        time.sleep(0.25)
        drv.find_element_by_class_name("chevron-cell").click()
        el = (
            drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        assert "Tarkistussumma" in el.text  # nosec
