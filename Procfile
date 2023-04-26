redis: docker run --rm --env-file ${PWD}/.env -p ${SWIFT_UI_REDIS_PORT}:${SWIFT_UI_REDIS_PORT} redis:7-bullseye
db: docker run --rm -v ${PWD}/.github/config/init-project-db.sh:/docker-entrypoint-initdb.d/init-user-db.sh --env-file ${PWD}/.env -p 5432:5432 postgres:14-bullseye
keystone: docker run --rm -p $KEYSTONE_PORT:5000 -p $SWIFT_PORT:8080 --env S6_LOGGING=0 --name keystone-swift ghcr.io/cscfi/docker-keystone-swift:latest
vault: "${PWD}"/scripts/vault.sh

# Commands to run without trusted TLS
# ui:       gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${UI_PORT}      swift_browser_ui.ui.server:servinit
# upload:   gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${UPLOAD_PORT}  swift_browser_ui.upload.server:servinit
# sharing:  gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${SHARING_PORT} swift_browser_ui.sharing.server:init_server
# request:  gunicorn --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${REQUEST_PORT} swift_browser_ui.request.server:init_server
# frontend: SWIFT_UI_SECURE_WEBSOCKET="" ALLOWED_HOSTS=${SWIFT_UI_FRONTEND_ALLOW_HOSTS} SWIFT_UI_TLS_PORT=${SWIFT_UI_TLS_PORT} SWIFT_UI_TLS_HOST=${SWIFT_UI_TLS_HOST} PORT=${FRONTEND_PORT} BACKEND_PORT=${BACKEND_PORT} pnpm --prefix swift_browser_ui_frontend/ run serve

# Commands to run with trusted TLS
ui:       gunicorn --forwarded-allow-ips="${DOCKER_NETWORK_SEGMENT}" --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${UI_PORT}      swift_browser_ui.ui.server:servinit
upload:   gunicorn --forwarded-allow-ips="${DOCKER_NETWORK_SEGMENT}" --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${UPLOAD_PORT}  swift_browser_ui.upload.server:servinit
sharing:  gunicorn --forwarded-allow-ips="${DOCKER_NETWORK_SEGMENT}" --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${SHARING_PORT} swift_browser_ui.sharing.server:init_server
request:  gunicorn --forwarded-allow-ips="${DOCKER_NETWORK_SEGMENT}" --reload --worker-class aiohttp.GunicornUVLoopWebWorker --workers 1 --log-level debug --graceful-timeout 60 --timeout 120 --bind ${HOST}:${REQUEST_PORT} swift_browser_ui.request.server:init_server
frontend: SWIFT_UI_SECURE_WEBSOCKET=s ALLOWED_HOSTS=${SWIFT_UI_FRONTEND_ALLOW_HOSTS} SWIFT_UI_TLS_PORT=${SWIFT_UI_TLS_PORT} SWIFT_UI_TLS_HOST=${SWIFT_UI_TLS_HOST} PORT=${FRONTEND_PORT} BACKEND_PORT=${BACKEND_PORT} pnpm --prefix swift_browser_ui_frontend/ run serve
proxy: docker run --rm --env-file ${PWD}/.env -p ${SWIFT_UI_TLS_PORT}:${SWIFT_UI_TLS_PORT} -p 9443:9443 -p 10443:10443 -p 11443:11443 --name swiftui-dev-proxy swift-browser-ui:swiftui-dev-proxy
