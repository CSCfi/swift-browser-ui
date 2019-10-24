"""Sharing backend database implementation."""


import os
import time

import psycopg2


class DBConn:
    """Class for the account sharing database functionality."""

    def __init__(self):
        """."""
        self.conn = psycopg2.connect(
            password=os.environ.get("SHARING_DB_PASSWORD", None),
            user=os.environ.get("SHARING_DB_USER", "sharing"),
            host=os.environ.get("SHARING_DB_HOST", "localhost"),
            dbname=os.environ.get("SHARING_DB_NAME", "swiftsharing")
        )

    def close(self):
        """."""
        self.conn.close()

    def _init_db(self):
        """Create the database with the wanted schema if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            BEGIN TRANSACTION;
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
            END;
        """)
        cursor.close()

    def add_share(self, owner, container, userlist, access, address):
        """Add a share action to the database."""
        with self.conn.cursor() as cursor:
            for key in userlist:
                cursor.execute("""
                    INSERT INTO Shares (
                        container,
                        container_owner,
                        recipient,
                        r_read,
                        r_write,
                        sharingdate,
                        address
                    ) VALUES (
                        %s, %s, %s, %s, %s, NOW(), %s
                    );
                """, (
                    container,
                    owner,
                    key,
                    "r" in access,
                    "w" in access,
                    address,
                ))
            cursor.execute("COMMIT;")
        return True

    def edit_share(self, owner, container, userlist, access):
        """."""
        with self.conn.cursor() as cursor:
            for key in userlist:
                cursor.execute("""
                    UPDATE Shares
                    SET
                        r_read = %s,
                        r_write = %s
                    WHERE
                        container = %s AND
                        container_owner = %s AND
                        recipient = %s
                    ;
                """, (
                    "r" in access,
                    "w" in access,
                    container,
                    owner,
                    key,
                ))
            cursor.execute("COMMIT;")
        return True

    def delete_share(self, owner, container, userlist):
        """."""
        with self.conn.cursor() as cursor:
            for key in userlist:
                cursor.execute("""
                    DELETE FROM Shares
                    WHERE
                        container = %s AND
                        container_owner = %s AND
                        recipient = %s
                    ;
                """, (
                    container,
                    owner,
                    key,
                ))
            cursor.execute("COMMIT;")
        return True

    def get_access_list(self, user):
        """."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT container, container_owner
                FROM Shares
                WHERE recipient = %s
                ;
            """, (
                user,
            ))

            return [
                {"container": i[0], "owner": i[1]}
                for i in cursor.fetchall()
            ]

    def get_shared_list(self, user):
        """."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT container
                FROM Shares
                WHERE container_owner = %s
            """, (
                user,
            ))

            return [
                {"container": i[0]}
                for i in cursor.fetchall()
            ]

    def get_access_container_details(self, user, owner, container):
        """."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    container,
                    container_owner,
                    recipient,
                    address,
                    r_read,
                    r_write
                FROM Shares
                WHERE
                    container_owner = %s AND
                    container = %s AND
                    recipient = %s
                ;
            """, (
                owner,
                container,
                user,
            ))

            query = cursor.fetchone()
            access = []

            if query[4]:
                access.append("r")
            if query[5]:
                access.append("w")

            return {
                "container": query[0],
                "owner": query[1],
                "sharedTo": query[2],
                "address": query[3],
                "access": access,
            }

    def get_shared_container_details(self, owner, container):
        """."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    container,
                    container_owner,
                    recipient,
                    address,
                    r_read,
                    r_write
                FROM Shares
                WHERE
                    container_owner = %s AND
                    container = %s
                ;
            """, (
                owner,
                container,
            ))

            query = cursor.fetchall()
            ret = []
            for i in query:
                access = []
                if i[4]:
                    access.append("r")
                if i[5]:
                    access.append("w")

                ret.append({
                    "container": i[0],
                    "owner": i[1],
                    "sharedTo": i[2],
                    "address": i[3],
                    "access": access,
                })
            return ret
