"""Sharing backend database implementation."""


import os

import asyncpg


class DBConn:
    """Class for the account sharing database functionality."""

    def __init__(self):
        """."""
        self.conn = None

    async def open(self):
        """."""
        self.conn = await asyncpg.connect(
            password=os.environ.get("SHARING_DB_PASSWORD", None),
            user=os.environ.get("SHARING_DB_USER", "sharing"),
            host=os.environ.get("SHARING_DB_HOST", "localhost"),
            database=os.environ.get("SHARING_DB_NAME", "swiftsharing")
        )

    async def close(self):
        """."""
        await self.conn.close()

    async def _init_db(self):
        """Create the database with the wanted schema if it doesn't exist."""
        async with self.conn.transaction():
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS Shares(
                    container TEXT,
                    container_owner TEXT,
                    recipient TEXT,
                    r_read BOOL,
                    r_write BOOL,
                    sharingdate TIMESTAMP,
                    address TEXT           NOT NULL,
                    PRIMARY KEY(container, container_owner, recipient)
                );
                CREATE TABLE IF NOT EXISTS Requests_FIMM(
                    batch TEXT,
                    recipient TEXT         NOT NULL,
                    container_owner TEXT   NOT NULL,
                    PRIMARY KEY(batch)
                );
            """)

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
        """."""
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
        """."""
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
        """."""
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
        """."""
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
        """."""
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
        """."""
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
