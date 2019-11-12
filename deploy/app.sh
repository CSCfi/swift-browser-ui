#!/bin/bash

THE_HOST=${HOST:="0.0.0.0"}
THE_PORT=${PORT:="9091"}

echo "Start swift-sharing-request backend"

gunicorn swift_sharing_request.server:init_server \
    --bind $THE_HOST:$THE_PORT \
    --worker-class aiohttp.GunicornUVLoopWebWorker \
    --workers 1 \
