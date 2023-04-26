path "c4ghtransit/keys/*" {
  capabilities = ["create", "update", "read"]
}
path "c4ghtransit/whitelist/*" {
  capabilities = ["create", "update", "read", "delete", "list"]
}
path "c4ghtransit/files/*" {
  capabilities = ["create", "update", "read", "delete", "list"]
}
path "c4ghtransit/sharing/*" {
  capabilities = ["create", "update", "read", "delete", "list"]
}
