![Javascript ESLint check](https://github.com/CSCfi/swift-x-account-sharing/workflows/Javascript%20ESLint%20check/badge.svg)
![Python style check](https://github.com/CSCfi/swift-x-account-sharing/workflows/Python%20style%20check/badge.svg)
![Python Unit Tests](https://github.com/CSCfi/swift-x-account-sharing/workflows/Python%20Unit%20Tests/badge.svg)

### swift-x-account-sharing – OS swift container sharing backend
Openstack Swift Access Control Lists don't natively implement querying
for containers that are shared for specific user. (i.e. if the user has
access to these containers on the object storage platform) This backend
is meant to be used as a workaround to implement the functionality, as
it is needed in some use cases.

The backend contains a database for managing the information on which
containers have been shared, by whom and to whom. The backend is meant
to be used as a solution to centrally share the container access
information in a given user pool, and thus isn't baked into the Openstack
native command line tools.

The default port for the service is 9090.

### Usage
```pip install . && swift-x-account-sharing```

The swift-x-account-sharing can use two different database styles for
storing the sharing information. The software defaults to an in-memory
database implemented in Python, but the preferred alternative for
production is PostgreSQL.

The PostgreSQL implementation can be enabled via environment variables,
that are
* SHARING_DB_POSTGRES; if found in environment, uses PostgreSQL.
* SHARING_DB_PASSWORD; REQUIRED; The password used for connecting to the
  database.
* SHARING_DB_USER; DEFAULT: sharing; The user used for the database
  access.
* SHARING_DB_HOST; DEFAULT: localhost; The host of the database server.
* SHARING_DB_NAME; DEFAULT: swiftsharing; The database that the backend
  needs to connect to.

### Access
The backend can be accessed with the API specified in the [API_spec.yml](docs/API_spec.yml)
file, and also with the binding modules contained in the `bindings`
directory.
