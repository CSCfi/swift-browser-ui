"""Sharing backend database implementation."""


import os
import logging
import asyncio
import random
import typing

import asyncpg


MODULE_LOGGER = logging.getLogger("db")
MODULE_LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class DBConn:
    """Class for the account sharing database functionality."""

    def __init__(self) -> None:
        """Initialize connection variable."""
        self.conn: asyncpg.connection.Connection = None
        self.log = MODULE_LOGGER

    def erase(self) -> None:
        """Erase the connection."""
        self.conn = None

    async def open(self) -> None:
        """Initialize the database connection."""
        while self.conn is None:
            try:
                self.conn = await asyncpg.connect(
                    password=os.environ.get("SHARING_DB_PASSWORD", None),
                    user=os.environ.get("SHARING_DB_USER", "sharing"),
                    host=os.environ.get("SHARING_DB_HOST", "localhost"),
                    database=os.environ.get("SHARING_DB_NAME", "swiftsharing"),
                )
            except (ConnectionError, OSError) as exp:
                self.conn = None
                slp = random.randint(5, 15)  # nosec
                self.log.error(
                    "Failed to establish database connection. "
                    "Retrying in %s seconds...",
                    slp,
                )
                self.log.log(logging.ERROR, "Failure information: %s", str(exp))
                await asyncio.sleep(slp)
            except asyncpg.InvalidPasswordError as exp:
                self.log.log(
                    logging.ERROR, "Invalid password for database. Info: %s", str(exp)
                )
                self.log.log(
                    logging.ERROR,
                    "User: %s",
                    os.environ.get("SHARING_DB_USER", "request"),
                )
                self.conn = None
                slp = random.randint(5, 15)  # nosec
                await asyncio.sleep(slp)

    async def close(self) -> None:
        """Safely close the database connection."""
        if self.conn is not None:
            await self.conn.close()

    async def add_share(
        self,
        owner: str,
        container: str,
        userlist: typing.List[str],
        access: typing.List[str],
        address: str,
    ) -> bool:
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

    async def edit_share(
        self,
        owner: str,
        container: str,
        userlist: typing.List[str],
        access: typing.List[str],
    ) -> bool:
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

    async def delete_share(
        self, owner: str, container: str, userlist: typing.List[str]
    ) -> bool:
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

    async def delete_container_shares(self, owner: str, container: str) -> bool:
        """Delete all shares for a container in the database."""
        async with self.conn.transaction():
            await self.conn.execute(
                """
                DELETE FROM Shares
                WHERE
                    container = $1 AND
                    container_owner = $2
                ;
                """,
                container,
                owner,
            )
        return True

    async def get_access_list(self, user: str) -> typing.List[dict]:
        """Get the containers shared to the specified user."""
        query = await self.conn.fetch(
            """
            SELECT container, container_owner, sharingdate
            FROM Shares
            WHERE recipient = $1
            ;
            """,
            user,
        )

        return [
            {
                "container": i["container"],
                "owner": i["container_owner"],
                "sharingdate": i["sharingdate"].strftime("%d %b %Y"),
            }
            for i in query
        ]

    async def get_shared_list(self, user: str) -> typing.List[str]:
        """Get the containers that the user has shared."""
        query = await self.conn.fetch(
            """
            SELECT DISTINCT
                container
            FROM Shares
            WHERE container_owner = $1
            """,
            user,
        )

        return [i["container"] for i in query]

    async def get_access_container_details(
        self, user: str, owner: str, container: str
    ) -> dict:
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

    async def get_shared_container_details(
        self, owner: str, container: str
    ) -> typing.List[dict]:
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

            ret.append(
                {
                    "container": i["container"],
                    "owner": i["container_owner"],
                    "sharedTo": i["recipient"],
                    "address": i["address"],
                    "access": access,
                }
            )
        return ret

    async def get_tokens(self, token_owner: str) -> typing.List[dict]:
        """Get tokens created for a project."""
        query = await self.conn.fetch(
            """
            SELECT *
            FROM Tokens
            WHERE token_owner = $1
            ;
            """,
            token_owner,
        )
        return list(query)

    async def revoke_token(self, token_owner: str, token_identifier: str) -> None:
        """Remove a token from the database."""
        async with self.conn.transaction():
            await self.conn.execute(
                """
                DELETE FROM Tokens
                WHERE
                    token_owner = $1 AND
                    identifier = $2
                ;
                """,
                token_owner,
                token_identifier,
            )

    async def add_token(self, token_owner: str, token: str, identifier: str) -> None:
        """Add a token to the database."""
        async with self.conn.transaction():
            await self.conn.execute(
                """
                INSERT INTO Tokens(
                    token_owner,
                    token,
                    identifier
                ) VALUES (
                    $1, $2, $3
                )
                ;
                """,
                token_owner,
                token,
                identifier,
            )
