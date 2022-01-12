Web User Interface
==================
The user interface defaults to a container listing, showing all the containers
for the default active project of the user. The localization can be changed
from the button in the up-right corner.


User information page
---------------------
Behind the **User information** button in the front page, a user information
dashboard is displayed. The dashboard displays statistics about the current
resource usage, e.g.

    - Current billing unit consumption
    - Amount of containers and objects in a project
    - Total project data usage.

Additional information on different billing details is also provided, in the
links contained in the dashboard bottom tile.

.. figure:: ./_static/images/screenshot-dashboard
    :scale: 50%
    :alt: Picture of the user information dashboard
    :align: center

    Image of the user information dashboard in an example project.


Container page
--------------
The default front-page for the browser is the container listing, which will
default to the first project that Openstack proposes. This page shows the
containers available to be browsed, as well as general information about them.
The container can be opened with a double-click, or if the table row's active,
enter.

.. figure:: ./_static/images/screenshot-front-page
    :scale: 50%
    :alt: Picture of the container listing, depicting a focusable table with rows describing content.
    :align: center

    Image of the container listing for an example project.


Object page
-----------
Any container can be opened, and the contents viewed. The object page shows
information on the objects, e.g.

    - The object name
    - The object ETag
    - A download link for the object
    - Content type
    - Last date of modification

.. figure:: ./_static/images/screenshot-object-page
    :scale: 50%
    :alt: Picture of the object listing, depicting a focusable table with rows describing content.
    :align: center

    Image of the object listing for an example container.

Additional information is not shown by default, but can be opened with the
chevron located in the beginning of each row.

.. figure:: ./_static/images/screenshot-object-details
    :scale: 50%
    :alt: Picture of the object listing with additional details opened.
    :align: center

    Image of the object listing, showing the additional details.


Non-whitelisted mode
--------------------
When running a development environment that is not whitelisted to use the
WebSSO for logins, the following login page will be displayed. The page is
there to enable manual token delivery, since the server refuses to deliver
it automatically to untrusted platforms. (i.e. copying and pasting the
token)

.. figure:: ./_static/images/screenshot-login-page
    :scale: 50%
    :alt: Picture of the manual token delivery screen.
    :align: center

    Image of the manual token delivery login page.
