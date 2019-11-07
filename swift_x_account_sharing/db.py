"""Sharing backend database implementation."""


import os
import logging
import asyncio
import random

import asyncpg


class DBConn:
    """Class for the account sharing database functionality."""

    def __init__(self):
        """Initialize connection variable."""
        self.conn = None
        self.log = logging.getLogger("db")

    def erase(self):
        """Erase the connection."""
        self.conn = None

    async def open(self):
        """Initialize the database connection."""
        while self.conn is None:
            try:
                self.conn = await asyncpg.connect(
                    password=os.environ.get("SHARING_DB_PASSWORD", None),
                    user=os.environ.get("SHARING_DB_USER", "sharing"),
                    host=os.environ.get("SHARING_DB_HOST", "localhost"),
                    database=os.environ.get("SHARING_DB_NAME", "swiftsharing")
                )
            except (ConnectionError, OSError) as exp:
                self.conn = None
                slp = random.randint(5, 15)  # nosec
                self.log.error(
                    "Failed to establish database connection. "
                    "Retrying in %s seconds...",
                    slp
                )
                self.log.log(
                    logging.ERROR,
                    "Failure information: %s",
                    str(exp)
                )
                await asyncio.sleep(slp)
            except asyncpg.InvalidPasswordError as exp:
                self.log.log(
                    logging.ERROR,
                    "Invalid password for database. Info: %s",
                    str(exp)
                )
                self.log.log(
                    logging.ERROR,
                    "User: %s",
                    os.environ.get("SHARING_DB_USER", "request"),
                )
                self.conn = None
                slp = random.randint(5, 15)  # nosec
                await asyncio.sleep(slp)

    async def close(self):
        """Safely close the database connection."""
        if self.conn is not None:
            await self.conn.close()

    async def add_share(self, owner, container, userlist, access, address):
        """Add a share action to the database."""
        async with self.conn.transaction():
            for key in userlist:
                await self.conn.execute(
                    """
                    INSERT INTO Shares (
                        container,
                        container_owner,
                        recipient,
                        r_read,
                        r_write,
                        sharingdate,
                        address
                    ) VALUES (
                        $1, $2, $3, $4, $5, NOW(), $6
                    );
                    """,
                    container,
                    owner,
                    key,
                    "r" in access,
                    "w" in access,
                    address,
                )
        return True

    async def edit_share(self, owner, container, userlist, access):
        """Edit a share action in the database."""
        async with self.conn.transaction():
            for key in userlist:
                await self.conn.execute(
                    """
                    UPDATE Shares
                    SET
                        r_read = $1,
                        r_write = $2
                    WHERE
                        container = $3 AND
                        container_owner = $4 AND
                        recipient = $5
                    ;
                    """,
                    "r" in access,
                    "w" in access,
                    container,
                    owner,
                    key,
                )
        return True

    async def delete_share(self, owner, container, userlist):
        """Delete a share action from the database."""
        async with self.conn.transaction():
            for key in userlist:
                await self.conn.execute(
                    """
                    DELETE FROM Shares
                    WHERE
                        container = $1 AND
                        container_owner = $2 AND
                        recipient = $3
                    ;
                    """,
                    container,
                    owner,
                    key,
                )
        return True

    async def get_access_list(self, user):
        """Get the containers shared to the specified user."""
        query = await self.conn.fetch(
            """
            SELECT container, container_owner
            FROM Shares
            WHERE recipient = $1
            ;
            """,
            user,
        )

        return [
            {"container": i["container"], "owner": i["container_owner"]}
            for i in query
        ]

    async def get_shared_list(self, user):
        """Get the containers that the user has shared."""
        query = await self.conn.fetch(
            """
            SELECT DISTINCT container
            FROM Shares
            WHERE container_owner = $1
            """,
            user,
        )

        return [
            {"container": i["container"]}
            for i in query
        ]

    async def get_access_container_details(self, user, owner, container):
        """Get shared container details for share receiver."""
        query = await self.conn.fetchrow(
            """
            SELECT
                container,
                container_owner,
                recipient,
                address,
                r_read,
                r_write
            FROM Shares
            WHERE
                container_owner = $1 AND
                container = $2 AND
                recipient = $3
            ;
            """,
            owner,
            container,
            user,
        )

        access = []

        if query["r_read"]:
            access.append("r")
        if query["r_write"]:
            access.append("w")

        return {
            "container": query["container"],
            "owner": query["container_owner"],
            "sharedTo": query["recipient"],
            "address": query["address"],
            "access": access,
        }

    async def get_shared_container_details(self, owner, container):
        """Get shared container details for sharer."""
        query = await self.conn.fetch(
            """
            SELECT
                container,
                container_owner,
                recipient,
                address,
                r_read,
                r_write
            FROM Shares
            WHERE
                container_owner = $1 AND
                container = $2
            ;
            """,
            owner,
            container,
        )

        ret = []
        for i in query:
            access = []
            if i["r_read"]:
                access.append("r")
            if i["r_write"]:
                access.append("w")

            ret.append({
                "container": i["container"],
                "owner": i["container_owner"],
                "sharedTo": i["recipient"],
                "address": i["address"],
                "access": access,
            })
        return ret
