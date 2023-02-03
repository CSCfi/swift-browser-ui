### swift-request-backend
API for requesting access to swift containers, to enable more fluid container
sharing process, the main use being the abstraction of separation of the
project's user from the user's own.

### Usage
swift-sharing-request by default expects a database running on the local
machine in port 5432. If a database is not run on the local machine, the
relevant information on the database can be provided with the following
environment variables:

* `REQUEST_DB_PASSWORD`; **REQUIRED**: The password used for connecting to the
  database.
* `REQUEST_DB_USER`; **DEFAULT**: request; The user used for the database
  access.
* `REQUEST_DB_HOST`; **DEFAULT**: localhost; The host of the database server.
* `REQUEST_DB_PORT`; **DEFAULT**: 5432; The port of the database server.
* `REQUEST_DB_SSL`; **DEFAULT**: prefer; The SSL to connect to the database server.
* `REQUEST_DB_NAME`; **DEFAULT**: swiftrequest; The database that the backend needs to connect to.

Swift-sharing-request can be run with the following command after all the
requirements are met:
```
pip install . && swift-sharing-request
```
