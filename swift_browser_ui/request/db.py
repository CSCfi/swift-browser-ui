"""Module for sharing request database interface using postgres."""


import logging
import os
import typing
import asyncio
import random

import asyncpg


MODULE_LOGGER = logging.getLogger("db")
MODULE_LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class DBConn:
    """Class for handling sharing request database connection."""

    def __init__(self) -> None:
        """."""
        self.log = MODULE_LOGGER
        self.pool: asyncpg.Pool = None

    async def open(self) -> None:
        """Gracefully open the database."""
        while self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    password=os.environ.get("REQUEST_DB_PASSWORD", None),
                    user=os.environ.get("REQUEST_DB_USER", "request"),
                    host=os.environ.get("REQUEST_DB_HOST", "localhost"),
                    port=int(os.environ.get("REQUEST_DB_PORT", 5432)),
                    ssl=os.environ.get("REQUEST_DB_SSL", "prefer"),
                    database=os.environ.get("REQUEST_DB_DATABASE", "swiftrequest"),
                    min_size=os.environ.get("REQUEST_DB_MIN_CONNECTIONS", 0),
                    max_size=os.environ.get("REQUEST_DB_MAX_CONNECTIONS", 49),
                    timeout=os.environ.get("REQUEST_DB_TIMEOUT", 120),
                    command_timeout=os.environ.get("REQUEST_DB_COMMAND_TIMEOUT", 180),
                    max_inactive_connection_lifetime=os.environ.get(
                        "REQUEST_DB_MAX_INACTIVE_CONN_LIFETIME", 0
                    ),
                )
            except (ConnectionError, OSError):
                self.log.error(
                    "Failed to establish database connection. "
                    "Pool will retry reconnection automatically...",
                )
                await asyncio.sleep(random.randint(2, 5))  # nosec
            except asyncpg.exceptions.InvalidPasswordError:
                self.log.error("Invalid username or password for database.")
                await asyncio.sleep(random.randint(2, 5))  # nosec
            except asyncpg.exceptions.CannotConnectNowError:
                self.log.error("Database is not ready yet.")
                await asyncio.sleep(random.randint(2, 5))  # nosec

    async def close(self) -> None:
        """Gracefully close the database."""
        if self.pool is not None:
            await self.pool.close()

    def erase(self) -> None:
        """Immediately erase the connection."""
        self.pool.terminate()
        self.pool = None

    @staticmethod
    async def parse_query(query: typing.List[asyncpg.Record]) -> typing.List[dict]:
        """Parse a database query list to JSON serializable form."""
        return [
            {
                "container": rec["container"],
                "user": rec["recipient"],
                "owner": rec["container_owner"],
                "date": rec["created"].isoformat(),
            }
            for rec in query
        ]

    async def add_request(self, user: str, container: str, owner: str) -> bool:
        """Add an access request to the database."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
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
                    user,
                )
                return True

    async def get_request_owned(self, user: str) -> typing.List:
        """Get the requests owned by the getter."""
        query = await self.pool.fetch(
            """
            SELECT *
            FROM Requests
            WHERE container_owner = $1
            ;
            """,
            user,
        )
        return await self.parse_query(query)

    async def get_request_made(self, user: str) -> typing.List:
        """Get the requests made by the getter."""
        query = await self.pool.fetch(
            """
            SELECT *
            FROM Requests
            WHERE recipient = $1
            ;
            """,
            user,
        )
        return await self.parse_query(query)

    async def get_request_container(self, container: str) -> typing.List:
        """Get the requests made for a container."""
        query = await self.pool.fetch(
            """
            SELECT *
            FROM Requests
            WHERE container = $1
            ;
            """,
            container,
        )
        return await self.parse_query(query)

    async def delete_request(self, container: str, owner: str, recipient: str) -> bool:
        """Delete an access request from the database."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
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
                    recipient,
                )
            return True

    async def get_tokens(self, token_owner: str) -> typing.List[dict]:
        """Get tokens created for a project."""
        query = await self.pool.fetch(
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
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
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
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
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
