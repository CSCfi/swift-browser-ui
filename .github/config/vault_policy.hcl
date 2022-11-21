path "c4ghtransit/keys/*" {
  capabilities = ["create", "read"]
}
path "c4ghtransit/whitelist/*" {
  capabilities = ["create", "update", "read", "delete"]
}
path "c4ghtransit/files/*" {
  capabilities = ["create", "update", "read", "delete"]
}
