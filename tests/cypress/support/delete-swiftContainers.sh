#!/usr/bin/env bash

# For best result, replace $OS_AUTH_URL with the real url from your .env file

IFS=$'\n'

USERS=(swift admin)
PASSWORDS=(veryfast superuser)
#OS_AUTH_URL=http://0.0.0.0:5000/v3

for ((i=0; i<${#USERS[@]}; ++i )); do
    PROJECTS=$(openstack \
        --os-auth-url $OS_AUTH_URL \
        --os-username ${USERS[i]} \
        --os-password ${PASSWORDS[i]} \
        --os-identity-api-version 3 \
        project list --format value)

    for project in $PROJECTS; do
        # project is "id name", remove id
        PROJECT_NAME=${project##* }

        CONTAINERS=$(openstack \
            --os-auth-url $OS_AUTH_URL \
            --os-username ${USERS[i]} \
            --os-project-name $PROJECT_NAME \
            --os-password ${PASSWORDS[i]}  \
            --os-identity-api-version 3 \
            container list --all --format value)

        for container in $CONTAINERS; do
            openstack \
                --os-auth-url $OS_AUTH_URL \
                --os-username ${USERS[i]} \
                --os-project-name $PROJECT_NAME \
                --os-password ${PASSWORDS[i]} \
                --os-identity-api-version 3 \
                container delete --recursive $container
        done
    done
done
