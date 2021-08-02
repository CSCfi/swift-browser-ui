#!/bin/bash

THE_HOST=${HOST:="0.0.0.0"}
THE_PORT=${PORT:="9092"}

echo "Start swift-upload-runner backend"

gunicorn swift_browser_ui.upload.server:servinit \
    --bind $THE_HOST:$THE_PORT \
    --worker-class aiohttp.GunicornUVLoopWebWorker \
    --workers 1 \
