#!/usr/bin/env bash

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
