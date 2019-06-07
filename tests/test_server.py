"""
Module for testing s3browser.server
"""


import pytest
from s3browser.server import servinit


@pytest.mark.asyncio
async def test_servinit():
    """
    Function for testing server initialization function execution
    """
    # Don't really need much testing here, if the server initialization
    # executes to the end all is fine.
    app = servinit()
    assert app is not None  # nosec
