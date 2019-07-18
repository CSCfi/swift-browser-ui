"""Front-end tests for the object browser, firefox."""


import time


from .common import handle_firefox_ui_test as handle_ui_test
from .common import navigate_to_container_with_objects
from .common import check_download
from .common import switch_to_finnish
from .common import navigate_to_next_container_from_search
from .common import navigate_to_next_full_after_back


def test_download_from_random_bucket():
    """Test if file download link works and can be navigated to."""
    # Pylint is incorrect on the variable being unused
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_download(drv):
        # Find a container with stuff
        drv = navigate_to_container_with_objects(drv)
        time.sleep(0.25)
        assert check_download(drv)  # nosec


def test_download_from_random_bucket_fin():
    """Test if the previous file download test works with finnish local."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_download(drv):
        switch_to_finnish(drv)
        drv = navigate_to_container_with_objects(drv)
        time.sleep(0.25)
        assert check_download(drv)  # nosec


def test_find_file_chekcsums():
    """Test seeking file checksums from the table listing."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_checksum(drv):
        drv = navigate_to_container_with_objects(drv)
        time.sleep(0.25)
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
        time.sleep(0.1)
        switch_to_finnish(drv)
        time.sleep(0.1)
        drv = navigate_to_container_with_objects(drv)
        time.sleep(0.25)
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
        time.sleep(0.25)
        assert "test-container-3" in drv.current_url  # nosec
        time.sleep(0.2)


def test_long_user_session():
    """Test the UI for a longer session."""
    # pylint: disable=unused-variable
    @handle_ui_test
    def test_long_session(drv):
        time.sleep(0.1)
        drv.find_element_by_class_name("input").send_keys(
            "test-container-4"
        )
        time.sleep(0.25)
        navigate_to_next_container_from_search(drv)
        assert "test-container-4" in drv.current_url  # nosec
        time.sleep(0.1)
        drv.back()
        time.sleep(0.1)
        navigate_to_next_full_after_back(drv)
        time.sleep(0.25)
        assert check_download(drv)  # nosec
        time.sleep(0.1)
        drv.back()
        time.sleep(0.1)
        switch_to_finnish(drv)
        time.sleep(0.25)
        drv.find_element_by_link_text("test_user_id").click()
        time.sleep(0.1)
        assert "Not yet implemented" in drv.page_source  # nosec
        drv.back()
        time.sleep(0.1)
        navigate_to_next_full_after_back(drv)
        time.sleep(0.25)
        drv.find_element_by_class_name("chevron-cell").click()
        el = (
            drv.find_element_by_class_name("detail-container")
            .find_element_by_tag_name("ul")
            .find_element_by_tag_name("li")
        )
        assert "Tarkistussumma" in el.text  # nosec
