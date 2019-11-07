### swift-request-backend
API for requesting access to swift containers, to enable more fluid container
sharing process, the main use being the abstraction of separation of the
project's user from the user's own.

### Usage
swift-sharing-request by default expects a database running on the local
machine in port 5432. If a database is not run on the local machine, the
relevant information on the database can be provided with the following
environment variables:
```
REQUEST_DB_PASSWORD="database password"
REQUEST_DB_USER="database user"
REQUEST_DB_HOST="database host"
REQUEST_DB_DATABASE="the database used by swift-sharing-request"
```

Swift-sharing-request can be run with the following command after all the
requirements are met:
```
pip install . && swift-sharing-request
```
