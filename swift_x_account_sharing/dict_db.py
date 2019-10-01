"""Dictionary based database emulation for development purposes."""
# This same class will probably be used as a base for the functions
# translating the program queries to the actual database, meaning a the
# queries into the final database should probably require the same things.


import json


class InMemDB():
    """Class emulating an in memory database."""

    def __init__(self):
        """."""
        self.shares = []

    def export_to_file(self, filename):
        """Export the database to file."""
        with open(filename, "w") as f:
            f.write(json.dumps(self.shares))

    def load_from_file(self, filename):
        """Load the database from file."""
        with open(filename, "r") as f:
            self.shares = json.loads("".join(f.readlines()))

    def add_share(self, owner, container, userlist, access, address):
        """Add a share action to database."""
        # Now assuming that there are no duplicates
        for key in userlist:
            self.shares.append({
                "owner": owner,
                "container": container,
                "sharedTo": key,
                "access": access,
                "address": address
            })

    def remove_share(self, owner, container, userlist, access):
        """Remove a share action from the database."""
        new_shares = []
        # For now iterate over whole list
        for key in userlist:
            for i in self.shares:
                if (
                        i.owner == owner
                        and i.container == container
                        and i.sharedTo == key
                ):
                    new_access = []
                    if "-r" not in access:
                        new_access.append("r")
                    if "-w" not in access:
                        new_access.append("w")
                    if "-l" not in access:
                        new_access.append("l")
                    if new_access:
                        new_shares.append({
                            "owner": owner,
                            "container": container,
                            "sharedTo": key,
                            "access": new_access,
                            "address": i.address,
                        })
                    self.shares.remove(i)
        if new_shares:
            for i in new_shares:
                self.shares.append(i)

    def get_access_list(self, user):
        # Assume no duplicates
        """Get the containers that are shared to specified user."""
        access_list = []
        for i in self.shares:
            if i.sharedTo == user:
                access_list.append({
                    "container": i.container,
                    "owner": i.owner,
                })
        return access_list

    def get_shared_list(self, user):
        """Get the containers that the user has shared."""
        shared_list = []
        for i in self.shares:
            if i.owner == user:
                if i.container not in shared_list:
                    shared_list.append(i.container)
        return shared_list

    def get_access_container_details(self, user, owner, container):
        """Get shared container details for accessee."""
        # Required to be unique
        for i in self.shares:
            if (
                    i.owner == owner
                    and i.container == container
                    and i.sharedTo == user
            ):
                return i
        return None

    def get_shared_container_details(self, owner, container):
        """Get shared container details for sharer."""
        shared_containers = []
        for i in self.shares:
            if (
                    i.owner == owner
                    and i.container == container
            ):
                shared_containers.append(i)
        if not shared_containers:
            return None
        return {
            "owner": owner,
            "container": container,
            "sharedTo": [i.sharedTo for i in shared_containers],
            "access": shared_containers[0].access,
            "address": shared_containers[0].address
        }
