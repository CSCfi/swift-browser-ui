redis: docker run --env-file ${PWD}/.env -p ${SWIFT_UI_REDIS_PORT}:${SWIFT_UI_REDIS_PORT} redis:alpine
db: docker run -v ${PWD}/.github/config/init-project-db.sh:/docker-entrypoint-initdb.d/init-user-db.sh --env-file ${PWD}/.env -p 5432:5432 postgres:alpine
keystone: docker run --init --rm -p $KEYSTONE_PORT:5000 -p $SWIFT_PORT:8080 --env S6_LOGGING=0 --name keystone-swift keystone-swift
ui:       gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${UI_PORT}      swift_browser_ui.ui.server:servinit
upload:   gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${UPLOAD_PORT}  swift_browser_ui.upload.server:servinit
sharing:  gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${SHARING_PORT} swift_browser_ui.sharing.server:init_server
request:  gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${REQUEST_PORT} swift_browser_ui.request.server:init_server
frontend: PORT=$FRONTEND_PORT BACKEND_PORT=$BACKEND_PORT npm --prefix swift_browser_ui_frontend/ run serve
