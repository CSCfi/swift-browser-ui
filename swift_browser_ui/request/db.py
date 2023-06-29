"""Module for sharing request database interface using postgres."""


import logging
import os
import typing

import asyncpg

from swift_browser_ui.common.common_util import sleep_random

MODULE_LOGGER = logging.getLogger("db")
MODULE_LOGGER.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class DBConn:
    """Class for handling sharing request database connection."""

    def __init__(self) -> None:
        """."""
        self.log = MODULE_LOGGER
        self.pool: asyncpg.Pool | None = None

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
                    database=os.environ.get("REQUEST_DB_NAME", "swiftbrowserdb"),
                    min_size=int(os.environ.get("REQUEST_DB_MIN_CONNECTIONS", 0)),
                    max_size=int(os.environ.get("REQUEST_DB_MAX_CONNECTIONS", 49)),
                    timeout=int(os.environ.get("REQUEST_DB_TIMEOUT", 120)),
                    command_timeout=int(
                        os.environ.get("REQUEST_DB_COMMAND_TIMEOUT", 180)
                    ),
                    max_inactive_connection_lifetime=int(
                        os.environ.get("REQUEST_DB_MAX_INACTIVE_CONN_LIFETIME", 0)
                    ),
                )
            except (ConnectionError, OSError):
                self.log.error(
                    "Failed to establish database connection. "
                    "Pool will retry reconnection automatically...",
                )
                await sleep_random()
            except asyncpg.exceptions.InvalidPasswordError:
                self.log.error("Invalid username or password for database.")
                await sleep_random()
            except asyncpg.exceptions.CannotConnectNowError:
                self.log.error("Database is not ready yet.")
                await sleep_random()

    async def close(self) -> None:
        """Gracefully close the database."""
        if self.pool is not None:
            await self.pool.close()

    def erase(self) -> None:
        """Immediately erase the connection."""
        if self.pool is not None:
            self.pool.terminate()
            self.pool = None

    @staticmethod
    async def parse_query(
        query: typing.List[asyncpg.Record],
    ) -> typing.List[typing.Dict[str, typing.Any]]:
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
        if self.pool is not None:
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
        return False

    async def get_request_owned(
        self, user: str
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Get the requests owned by the getter."""
        if self.pool is not None:
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
        return []

    async def get_request_made(
        self, user: str
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Get the requests made by the getter."""
        if self.pool is not None:
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
        return []

    async def get_request_container(
        self, container: str
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Get the requests made for a container."""
        if self.pool is not None:
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
        return []

    async def delete_request(self, container: str, owner: str, recipient: str) -> bool:
        """Delete an access request from the database."""
        if self.pool is not None:
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
        return False
