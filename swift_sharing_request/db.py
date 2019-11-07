"""Module for sharing request database interface using postgres."""


import logging
import random
import asyncio
import os

import asyncpg


class DBConn:
    """Class for handling sharing request database connection."""

    def __init__(self):
        """."""
        self.log = logging.getLogger("db")
        self.conn = None

    async def open(self):
        """Gracefully open the database."""
        while self.conn is None:
            try:
                self.conn = await asyncpg.connect(
                    password=os.environ.get("REQUEST_DB_PASSWORD", None),
                    user=os.environ.get("REQUEST_DB_USER", "request"),
                    host=os.environ.get("REQUEST_DB_HOST", "localhost"),
                    database=os.environ.get("REQUEST_DB_DATABASE", "swiftrequest")
                )
            except (ConnectionError, OSError) as exp:
                self.conn = None
                slp = random.randint(5, 15)  # noseq
                self.log.log(
                    logging.ERROR,
                    "Failed to establish database connection. "
                    "Retrying in %d seconds...",
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
                    "User: %s, Password: %s",
                    os.environ.get("REQUEST_DB_USER", "request"),
                    os.environ.get("REQUEST_DB_PASSWORD", None)
                )
                self.conn = None
                slp = random.randint(5, 15)
                await asyncio.sleep(slp)

    async def close(self):
        """Gracefully close the database."""
        if self.conn is not None:
            await self.conn.close()

    async def erase(self):
        """Erase a failed connection."""
        self.conn = None

    async def add_request(self, user, container, owner):
        """Add an access request to the database."""
        async with self.conn.transaction():
            await self.conn.execute(
                """
                INSERT INTO Requests(
                    container,
                    container_owner,
                    recipient,
                    created
                ) VALUES (
                    $1, $2, $3, NOW()
                );
                """,
                container,
                owner,
                user
            )
            return True

    async def get_request_owned(self, user):
        """Get the requests owned by the getter."""
        query = await self.conn.fetch(
            """
            SELECT *
            FROM Requests
            WHERE container_owner = $1
            ;
            """,
            user
        )
        return [
            {
                "container": rec["container"],
                "user": rec["recipient"],
                "owner": rec["container_owner"],
                "date": rec["created"].isoformat(),
            } for rec in query
        ]

    async def get_request_made(self, user):
        """Get the requests made by the getter."""
        query = await self.conn.fetch(
            """
            SELECT *
            FROM Requests
            WHERE recipient = $1
            ;
            """,
            user
        )
        return [
            {
                "container": rec["container"],
                "user": rec["recipient"],
                "owner": rec["container_owner"],
                "date": rec["created"].isoformat(),
            } for rec in query
        ]

    async def get_request_container(self, container):
        """Get the requests made for a container."""
        query = await self.conn.fetch(
            """
            SELECT *
            FROM Requests
            WHERE container = $1
            ;
            """,
            container
        )
        return [
            {
                "container": rec["container"],
                "user": rec["recipient"],
                "owner": rec["container_owner"],
                "date": rec["created"].isoformat(),
            } for rec in query
        ]

    async def delete_request(self, container, owner, recipient):
        """Delete an access request from the database."""
        async with self.conn.transaction():
            await self.conn.execute(
                """
                DELETE FROM Requests
                WHERE
                    container = $1 AND
                    container_owner = $2 AND
                    recipient = $3
                ;
                """,
                container,
                owner,
                recipient
            )
        return True
