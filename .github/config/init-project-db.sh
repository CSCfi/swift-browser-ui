#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER sharing;
    CREATE USER request;
    CREATE DATABASE swiftsharing;
    CREATE DATABASE swiftrequest;
    GRANT ALL PRIVILEGES ON DATABASE swiftsharing TO sharing;
    GRANT ALL PRIVILEGES ON DATABASE swiftrequest TO request;
    ALTER USER sharing WITH PASSWORD '$SHARING_PASSWORD';
    ALTER USER request WITH PASSWORD '$REQUEST_PASSWORD';
EOSQL

psql -v ON_ERROR_STOP=1 --username "sharing" --dbname "swiftsharing" <<-EOSQL
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
    CREATE TABLE IF NOT EXISTS Tokens(
        token_owner TEXT,
        token TEXT,
        identifier TEXT,
        PRIMARY KEY(token_owner, identifier)
    );
EOSQL

psql -v ON_ERROR_STOP=1 --username "request" --dbname "swiftrequest" <<-EOSQL
    CREATE TABLE IF NOT EXISTS Requests(
        container TEXT,
        container_owner TEXT,
        recipient TEXT,
        created TIMESTAMP,
        PRIMARY KEY(container, container_owner, recipient)
    );
    CREATE TABLE IF NOT EXISTS Tokens(
        token_owner TEXT,
        token TEXT,
        identifier TEXT,
        PRIMARY KEY(token_owner, identifier)
    );
EOSQL
