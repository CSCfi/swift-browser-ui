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



Kubernetes Integration
----------------------

For use with Kubernetes we provide ``YAML`` configuration.

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
