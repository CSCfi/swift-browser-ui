#!/bin/sh

THE_HOST=${HOST:="0.0.0.0"}
THE_PORT=${PORT:="8080"}

echo 'Start object-browser application'

gunicorn swift_browser_ui.ui.server:servinit --bind $THE_HOST:$THE_PORT --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --graceful-timeout 60 --timeout 120
