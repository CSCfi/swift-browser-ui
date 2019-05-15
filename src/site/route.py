# -*- coding: utf-8 -*-

"""
Collective module for implementing all the project routes, that are currently
in use. Made with the primary purpose of providing a direct and clear picture
of which url points to which handler.

The handlers are arranged in order of importance (honestly though, it's an
opinion) and grouped by from which module they can be found. The imported
modules can be found in the beginning.
"""


import aiohttp.web


# The project module imports
import api
import login
# For now also import the frontend module, which won't be present in the final
# version. (The frontend consists of only static HTML, JavaScript and css and
# thus it can be hosted directly from the Nginx server)
import front


routel = []


# Add routes from the module API
routel.append([
    aiohttp.web.get(api.API_ENDPOINT + '/buckets', api.list_buckets),
    aiohttp.web.get(api.API_ENDPOINT + '/dload', api.download_object),
    aiohttp.web.get(api.API_ENDPOINT + '/objects', api.list_objects),
])

# Add routes from the module login
routel.append([

])

# Add routes from the module front
routel.append([
    aiohttp.web.get('/', front.index),
    aiohttp.web.get('/browse', front.browse),
    aiohttp.web.get('/login', front.login),
])
