Architecture
============
In this section we would like to emphasize some of the core parts of the
application and describe their inner-workings.

About login process
-------------------
The program uses the WebSSO support provided by `Openstack <https://www.openstack.org/>`_, whenever the support
has been implemented. At minimum the program requires the Openstack instance
that it's supposed to be used with to implement the federated authentication,
in which the non-WebSSO token delivery method can be used.

A collection of links to provide a recap of the things necessary to know about
Openstack WebSSO implementation:

* `Federated authentication API in Openstack <https://docs.openstack.org/keystone/pike/advanced-topics/federation/federated_identity.html>`_
* `WebSSO details conveniently explained (or how it works in the OS Horizon dashboard) <http://www.gazlene.net/demystifying-keystone-federation.html>`_
* `Openstack Horizon dashboard WebSSO guide <https://docs.openstack.org/keystone/pike/advanced-topics/federation/websso.html>`_

The login process follows an *almost ordinary* process of federated
authentication with SAML, but that is something we don't need to concern
ourselves with – Openstack identity API takes care of that. The manual
version works in much the same way, but the user is required to copy and
paste the token themselves, since Openstack refuses to redirect to untrusted
platforms.

.. figure:: ./_static/images/WebSSO_login.svg
    :scale: 66%
    :alt: Sequence diagram of the login process
    :align: center

    Sequence diagram of the login process.

API
---
.. hint::
    The API has several endpoints, which are documented here. The API can
    also be used with the convenience functions, located in the ``api.js``
    file.

.. note::
    All API queries expect an open session to Openstack, which meas the
    queries towards Openstack are correctly scoped to the open project
    without further information in the API query. This of course requires
    a valid session token to be present with every API call.

The following flowchart gives a generic image of the possible responses from
the API during normal usage.

.. figure:: ./_static/images/API_flow.svg
    :scale: 50%
    :alt: Flowchart of the simplified API execute routes.
    :align: center

    Flowchart of the simplified API execute routes upon query.

The api is documented in the api.yml file, that conforms to the OpenAPI
specification (the file can be rendered with the `swagger editor <https://editor.swagger.io/?url=https://raw.githubusercontent.com/CSCfi/swift-browser-ui/master/docs/_static/api.yml>`_):

