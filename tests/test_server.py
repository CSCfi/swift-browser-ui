"""
Module for testing s3browser.server, will also contain the tests for front.py
"""


import os
import pytest
from s3browser.server import servinit
from s3browser.settings import setd


# Set static folder in settings so it can be tested
setd['static_directory'] = os.getcwd() + '/s3browser_frontend'


@pytest.mark.asyncio
async def test_servinit():
    """
    Function for testing server initialization function execution
    """
    # Don't really need much testing here, if the server initialization
    # executes to the end all is fine.
    app = servinit()
    assert app is not None  # nosec


# After testing the server initialization, we can use the correctly starting
# server for testing other modules.
@pytest.fixture
def cli(loop, aiohttp_client):
    return loop.run_until_complete(aiohttp_client(servinit()))
