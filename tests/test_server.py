"""
Module for testing s3browser.server, will also contain the tests for front.py
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


# After testing the server initialization, we can use the correctly starting
# server for testing other modules.
@pytest.fixture
def cli(loop, aiohttp_client):
    return loop.run_until_complete(aiohttp_client(servinit()))


async def test_working_routes(cli):
    """
    Function for testing all the specified server routes. All routes need to
    work in order for the test to pass, i.e. no 404 is allowed from any of the
    specified routes in the application back-end.
    """
    # OPINION: this unit test will fail on the first encountered broken route,
    # and thus won't check the others. In my opinion it's fine, since the
    # broken routes can be fixed one at a time. Having all the route checks in
    # a single compact function is better overall. – Sampsa Penna
    response = await cli.get('/')
    assert response.status != 404  # nosec
    response = await cli.get('/browse')
    assert response.status != 404  # nosec
    response = await cli.get('/login')
    assert response.status != 404  # nosec
    response = await cli.get('/login/kill')
    assert response.status != 404  # nosec
    response = await cli.get('/login/front')
    assert response.status != 404  # nosec
    response = await cli.get('/login/rescope')
    assert response.status != 404  # nosec
    response = await cli.get('/api/buckets')
    assert response.status != 404  # nosec
    response = await cli.get('/api/objects')
    assert response.status != 404  # nosec
    response = await cli.get('/api/dload')
    assert response.status != 404  # nosec
    response = await cli.get('/api/username')
    assert response.status != 404  # nosec
    response = await cli.get('/api/projects')
    assert response.status != 404  # nosec
    # Test all the static folders as well
    response = await cli.get('/static/index.html')
    assert response.status != 404  # nosec
    response = await cli.get('/static/browse.html')
    assert response.status != 404  # nosec
    response = await cli.get('/static/login.html')
    assert response.status != 404  # nosec
    response = await cli.get('/static/css/login.css')
    assert response.status != 404  # nosec
    response = await cli.get('/static/css/browse.css')
    assert response.status != 404  # nosec
    response = await cli.get('/static/js/browse.js')
    assert response.status != 404  # nosec
    response = await cli.get('/static/js/btablecomp.js')
    assert response.status != 404  # nosec
