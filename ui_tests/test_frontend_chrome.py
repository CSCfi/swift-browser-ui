"""Front-end tests for the object browser, chrome."""


from .common import handle_chrome_ui_test as handle_ui_test
from .common import navigate_to_container_with_objects
from .common import check_download
from .common import switch_to_finnish


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
