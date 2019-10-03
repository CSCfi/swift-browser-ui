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
