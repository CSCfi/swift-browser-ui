#!/bin/bash

THE_HOST=${HOST:="0.0.0.0"}
THE_PORT=${PORT:="8080"}

echo 'Start object-browser application'

gunicorn s3browser.server:servinit --bind $THE_HOST:$THE_PORT --worker-class aiohttp.GunicornUVLoopWebWorker --workers 4