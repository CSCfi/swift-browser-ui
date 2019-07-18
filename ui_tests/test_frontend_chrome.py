"""Front-end tests for the object browser, chrome."""


import time


from .common import handle_chrome_ui_test as handle_ui_test
from .common import navigate_to_container_with_objects
from .common import check_download
from .common import switch_to_finnish
from .common import navigate_to_next_container_from_search


def test_download_from_random_bucket():
    """Test if file download link works and can be navigated to."""
    # Pylint is incorrect on the variable being unused
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_download(drv):
        # Find a container with stuff
        drv = navigate_to_container_with_objects(drv)
        assert check_download(drv)  # nosec


def test_download_from_random_bucket_fin():
    """Test if the previous file download test works with finnish local."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_download(drv):
        switch_to_finnish(drv)
        drv = navigate_to_container_with_objects(drv)
        assert check_download(drv)  # nosec


def test_find_file_chekcsums():
    """Test seeking file checksums from the table listing."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_checksum(drv):
        drv = navigate_to_container_with_objects(drv)
        drv.find_element_by_class_name("chevron-cell").click()
        el = (
            drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        assert "Hash" in el.text  # nosec


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


def test_search_a_container():
    """Test searching a specific container and navigating to it."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_search_bar(drv):
        drv.find_element_by_class_name("input").send_keys(
            "test-container-3"
        )
        time.sleep(0.25)
        navigate_to_next_container_from_search(drv)
        assert "test-container-3" in drv.current_url  # nosec
        time.sleep(0.1)
