#!/usr/bin/env bash

set -e

# This script starts and configures a vault server in development mode with c4ghtransit plugin enabled
# and applies the pre-defined configuration to work the the backend server

# The vault server replaces the bash process, so this script works well under a process manager

# Dependencies
# - swift-browser-ui
# - c4ghtransit
# - go
# - vault
# - correctly set environment variables

# get the root of swift-browser-ui
SCRIPT="$(realpath $0)"
SCRIPTS=$(dirname "$SCRIPT")
ROOT=$(dirname "$SCRIPTS")

# set paths of swift-browser-ui and c4gh-transit vault plugin
C4GH_TRANSIT_DIR=${C4GH_TRANSIT_DIR:-/tmp/c4gh-transit}
SWIFT_BROWSER_UI_DIR=${SWIFT_BROWSER_UI_DIR:-$ROOT}

function initVault {
    cd "$SWIFT_BROWSER_UI_DIR"
    export VAULT_ADDR='http://127.0.0.1:8200'
    vault login token=devroot
    vault auth enable approle
    vault secrets enable c4ghtransit
    vault policy write swiftbrowser "$SWIFT_BROWSER_UI_DIR"/.github/config/vault_policy.hcl
    vault write auth/approle/role/swiftbrowser secret_id_ttl=0 secret_id_num_uses=0 token_ttl=5m token_max_ttl=5m token_num_uses=0 token_policies=swiftbrowser role_id=swiftbrowserui
    vault write -format=json -f auth/approle/role/swiftbrowser/custom-secret-id secret_id=swiftui
}

# pull the plugin if the directory doesn't exist
if [ ! -d "$C4GH_TRANSIT_DIR" ]; then
    git clone ssh://git@gitlab.ci.csc.fi:10022/sds-dev/c4gh-transit.git "$C4GH_TRANSIT_DIR"
fi

# update the code and build the plugin
cd "$C4GH_TRANSIT_DIR"
git pull
mkdir -p vault/plugins
go build -v -o vault/plugins/c4ghtransit c4ghtransit/cmd/c4ghtransit/main.go

# setup vault for swift-browser-ui in the background, after the server is up
(sleep 1; initVault) 2>&1 &

# start vault server in development mode
VAULT_LOG_LEVEL=ERROR exec vault server -dev -dev-plugin-dir=vault/plugins -dev-root-token-id="devroot"
