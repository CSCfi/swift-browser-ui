"""Module for sharing request database interface using postgres."""


import logging
import random
import asyncio
import os
import typing

import asyncpg
import aiohttp.web


MODULE_LOGGER = logging.getLogger("db")
MODULE_LOGGER.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


def handle_dropped_connection(
        request: aiohttp.web.Request
) -> None:
    """Handle dropped database connection."""
    MODULE_LOGGER.log(
        logging.ERROR,
        "Lost database connection, reconnecting..."
    )
    request.app["db_conn"].erase()
    asyncio.ensure_future(
        request.app["db_conn"].open()
    )
    raise aiohttp.web.HTTPServiceUnavailable(
        reason="No database connection."
    )


class DBConn:
    """Class for handling sharing request database connection."""

    def __init__(self) -> None:
        """."""
        self.log = MODULE_LOGGER
        self.conn: asyncpg.connection.Connection = None

    async def open(self) -> None:
        """Gracefully open the database."""
        while self.conn is None:
            try:
                self.conn = await asyncpg.connect(
                    password=os.environ.get("REQUEST_DB_PASSWORD", None),
                    user=os.environ.get("REQUEST_DB_USER", "request"),
                    host=os.environ.get("REQUEST_DB_HOST", "localhost"),
                    database=os.environ.get("REQUEST_DB_DATABASE",
                                            "swiftrequest")
                )
            except (ConnectionError, OSError) as exp:
                self.conn = None
                slp = random.randint(5, 15)  # nosec
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
                    "User: %s",
                    os.environ.get("REQUEST_DB_USER", "request"),
                )
                self.conn = None
                slp = random.randint(5, 15)  # nosec
                await asyncio.sleep(slp)

    async def close(self) -> None:
        """Gracefully close the database."""
        if self.conn is not None:
            await self.conn.close()

    def erase(self) -> None:
        """Erase a failed connection."""
        self.conn = None

    @staticmethod
    async def parse_query(
        query: typing.List[asyncpg.Record]
    ) -> typing.List[dict]:
        """Parse a database query list to JSON serializable form."""
        return [
            {
                "container": rec["container"],
                "user": rec["recipient"],
                "owner": rec["container_owner"],
                "date": rec["created"].isoformat(),
            } for rec in query
        ]

    async def add_request(
        self, user: str,
        container: str,
        owner: str
    ) -> bool:
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

    async def get_request_owned(
        self,
        user: str
    ) -> typing.List:
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
        return await self.parse_query(query)

    async def get_request_made(
        self,
        user: str
    ) -> typing.List:
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
        return await self.parse_query(query)

    async def get_request_container(
        self,
        container: str
    ) -> typing.List:
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
        return await self.parse_query(query)

    async def delete_request(
        self,
        container: str,
        owner: str,
        recipient: str
    ) -> bool:
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

    async def get_tokens(
            self,
            token_owner: str
    ) -> typing.List[dict]:
        """Get tokens created for a project."""
        query = await self.conn.fetch(
            """
            SELECT *
            FROM Tokens
            WHERE token_owner = $1
            ;
            """,
            token_owner
        )
        return list(query)

    async def revoke_token(
            self,
            token_owner: str,
            token_identifier: str
    ) -> None:
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
                token_identifier
            )

    async def add_token(
            self,
            token_owner: str,
            token: str,
            identifier: str
    ) -> None:
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
                identifier
            )
