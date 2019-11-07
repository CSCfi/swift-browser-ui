#!/bin/bash

THE_HOST=${HOST:="0.0.0.0"}
THE_PORT=${PORT:="9090"}

echo "Start swift-x-account-sharing backend"

gunicorn swift_x_account_sharing.server:init_server \
    --bind $THE_HOST:$THE_PORT \
    --worker-class aiohttp.GunicornUVLoopWebWorker \
    --workers 4 \
    --timeout 30
