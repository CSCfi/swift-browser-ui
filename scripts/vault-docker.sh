#!/usr/bin/env sh

set -e

cd /gosrc
mkdir -p /vault/plugins
go build -v -o /vault/plugins/c4ghtransit c4ghtransit/cmd/c4ghtransit/main.go

cd /vault

function initVault {
    export VAULT_ADDR="http://127.0.0.1:8200"
    wget --retry-connrefused --waitretry=1 --timeout=60 --spider $VAULT_ADDR/v1/sys/health?standbyok=true
    vault login token=devroot
    vault auth enable approle
    vault secrets enable c4ghtransit
    vault policy write swiftbrowser /vault_policy.hcl
    vault write auth/approle/role/swiftbrowser secret_id_ttl=0 secret_id_num_uses=0 token_ttl=5m token_max_ttl=5m token_num_uses=0 token_policies=swiftbrowser role_id=swiftbrowserui
    vault write -format=json -f auth/approle/role/swiftbrowser/custom-secret-id secret_id=swiftui
}

initVault 2>&1 &

VAULT_LOG_LEVEL=ERROR exec vault server -dev -dev-listen-address="0.0.0.0:8200" -dev-plugin-dir=/vault/plugins -dev-root-token-id="devroot"
