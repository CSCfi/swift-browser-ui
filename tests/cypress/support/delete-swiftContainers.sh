#!/usr/bin/env bash

# For best result, replace $OS_AUTH_URL with the real url from your .env file

IFS=$'\n'

CONTAINERS=$(openstack \
    --os-auth-url $OS_AUTH_URL \
    --os-username swift \
    --os-project-name service \
    --os-password veryfast \
    --os-identity-api-version 3 \
    container list --all --format value)

for container in $CONTAINERS; do
    openstack \
        --os-auth-url $OS_AUTH_URL \
        --os-username swift \
        --os-project-name service \
        --os-password veryfast \
        --os-identity-api-version 3 \
        container delete --recursive $container
done
