Deployment
==========

The recommended means of deployment for a production web server via
a container image (e.g. Docker image).
In this section we illustrate several means of building and running a
the ``swift-browser-ui`` application via a Docker container image.

Dockerfile
----------

Using vanilla docker in order to build the image - the tag can be customised:

.. code-block:: console

    $ git clone https://github.com/CSCfi/swift-browser-ui/
    $ docker build -t cscfi/swift-ui .
    $ docker run -p 8080:8080 cscfi/swift-ui
    $ # or with environment variables
    $ docker run -p 8080:8080 \
                 -e BROWSER_START_AUTH_ENDPOINT_URL=https://pouta.csc.fi:5001/v3 \
                 cscfi/swift-ui

Database for sharing functionality
----------------------------------
Both ``swift-x-account-sharing`` and ``swift-sharing-request`` services need
access to a PostgreSQL database in order to work. In a usual deployment this
is done within a containerized stack. Necessary files to build a database
container for testing can be found in the `deployment example repository. <https://github.com/CSCfi/swift-ui-deployment/>`_
The file ``init-project-db.sh`` contains the necessary input to build the DB
schema, and the same commands can be used to build the schema into an existing
database server (as is the case when running on openshift using a base image
for the database)

Sharing functionality back-end
------------------------------
Sharing functionality should be run by running it in a container. Easiest
way to do this is to use the docker-compose fields provided in the 
`deployment example repository. <https://github.com/CSCfi/swift-ui-deployment/>`_
The sharing functionality requires the following environment variables to be
present in order to work:

+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| Environment variable         | Default      | Required | Description                                                                         |
+==============================+==============+==========+=====================================================================================+
| ``SWIFT_UI_API_AUTH_TOKENS`` |              | True     | Comma separated list of master tokens that can be used for signing the API requests |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``SHARING_DB_NAME``          | swiftsharing |          | Name for the sharing functionality database                                         |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``SHARING_DB_USER``          | sharing      |          | User used in connecting to the sharing functionality database                       |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``SHARING_DB_HOST``          |              | True     | Sharing functionality database address/hostname                                     |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``SHARING_DB_PASSWORD``      |              | True     | Sharing functionality database password                                             |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+

Shared access request back-end
------------------------------
Shared access request functionality should be run by running it in a
container. Easiest way to do this is to use the docker-compose files provided
in the `deployment example repository. <https://github.com/CSCfi/swift-ui-deployment/>`_
The shared access request functionality requires the following environment variables
to be present in order to work:

+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| Environment variable         | Default      | Required | Description                                                                         |
+==============================+==============+==========+=====================================================================================+
| ``SWIFT_UI_API_AUTH_TOKENS`` |              | True     | Comma separated list of master tokens that can be used for signing the API requests |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``REQUEST_DB_NAME``          | swiftrequest |          | Name for the shared access request functionality database                           |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``REQUEST_DB_USER``          | request      |          | User used in connecting to the shared access request functionality database         |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``REQUEST_DB_HOST``          |              | True     | Shared access request functionality database address/hostname                       |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+
| ``REQUEST_DB_PASSWORD``      |              | True     | Shared access request functionality database password                               |
+------------------------------+--------------+----------+-------------------------------------------------------------------------------------+

Upload runner back-end
----------------------
SwiftUI upload runner should be run by running it in a container. Easiest way
to do this is to use the docker-compose files provided in the 
`deployment example repository. <https://github.com/CSCfi/swift-ui-deployment/>`_
The upload runner requires the following environment variables to be present
in order to work:

+-------------------------------------+---------+----------+-------------------------------------------------------------------------------------------------------------+
| Environment variable                | Default | Required | Description                                                                                                 |
+=====================================+=========+==========+=============================================================================================================+
| ``SWIFT_UI_API_AUTH_TOKENS``        |         | True     | Comma separated list of master tokens that can be used for signing the API requests                         |
+-------------------------------------+---------+----------+-------------------------------------------------------------------------------------------------------------+
| ``BROWSER_START_AUTH_ENDPOINT_URL`` |         |          | Openstack keystone endpoint for authentication – can also be specified with OS_AUTH_URL                     |
+-------------------------------------+---------+----------+-------------------------------------------------------------------------------------------------------------+
| ``OS_AUTH_URL``                     |         |          | Openstack keystone endpoint for authentication – can also be specified with BROWSER_START_AUTH_ENDPOINT_URL |
+-------------------------------------+---------+----------+-------------------------------------------------------------------------------------------------------------+

The authentication information can also be gotten through sourcing any
Openstack credential v3 file, the password is not necessary as only the
authentication endpoint information will be used.

Kubernetes Integration
----------------------

For use with Kubernetes we provide ``YAML`` configuration. Further
configuration files are provided in `deployment example repository <https://github.com/CSCfi/swift-ui-deployment/>`_

.. code-block:: yaml

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      labels:
        role: swiftui
      name: swiftui
      namespace: swiftui
    spec:
      selector:
        matchLabels:
          app: swiftui
      template:
        metadata:
          labels:
            app: swiftui
            role: swiftui
        spec:
          containers:
            - image: cscfi/swift-ui
              imagePullPolicy: Always
              name: swiftui
              ports:
                - containerPort: 8080
                  name: swiftui
                  protocol: TCP
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: swiftui
      labels:
        app: swiftui
    spec:
      type: NodePort
      ports:
        - port: 8080
          targetPort: 8080
          protocol: TCP
          name: web
      selector:
        app: swiftui
