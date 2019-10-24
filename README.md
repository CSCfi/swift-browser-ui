[![Build Status](https://travis-ci.com/CSCfi/swift-x-account-sharing.svg?branch=master)](https://travis-ci.com/CSCfi/swift-x-account-sharing)

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

### Access
The backend can be accessed with the API specified in the [API_spec.yml](docs/API_spec.yml)
file, and also with the binding modules contained in the `bindings`
directory.
