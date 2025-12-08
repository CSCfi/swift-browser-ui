#!/bin/env bash


set -eu


# Script for generating a development CA, and develompent time browser profiles
# for accessing the local services using the Dev CA.

: ${DEV_UI_HOSTNAME:="sd-connect.devenv"}
: ${DEV_KEYSTONE_HOSTNAME:="keystone.devenv"}
: ${DEV_CEPH_HOSTNAME:="rgw.devenv"}

: ${DEV_PROXY_IP:="172.31.2.2"}

: ${DEV_CEPH_ADDRESS:="172.31.0.5"}
: ${DEV_CEPH_GATEWAY:="172.31.0.1"}


function ensure_dev_res_dir {
    mkdir -p "$PWD/.devres/ca/csrs"
    mkdir -p "$PWD/.devres/pki"
}


function gen_hosts {
    cat > "$PWD/.devres/hosts" <<EOF
127.0.0.1 localhost
127.0.1.1 csc2

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

$DEV_CEPH_ADDRESS $DEV_CEPH_HOSTNAME
127.0.0.1 $DEV_KEYSTONE_HOSTNAME
127.0.0.1 $DEV_UI_HOSTNAME
EOF
}


function gen_ceph_hosts {
    cat > "$PWD/.devres/hosts_ceph_vm" <<EOF
127.0.0.1 localhost
127.0.1.1 csc2

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

$DEV_CEPH_ADDRESS $DEV_CEPH_HOSTNAME
$DEV_CEPH_GATEWAY $DEV_KEYSTONE_HOSTNAME
$DEV_CEPH_GATEWAY $DEV_UI_HOSTNAME
EOF
}



function gen_csr {
    cat > "$PWD/.devres/ca/csrs/$1.csr.conf" << EOF
[ req ]
default_bits = 4096
default_keyfile = $PWD/.devres/pki/$1.key
encrypt_key = no

default_md = sha256

prompt = no

utf8 = yes

distinguished_name = $1

req_extensions = v3_extensions

[ $1 ]
C = FI
ST = Espoo
L = Espoo
O  = CSC
CN = $1

[ v3_extensions ]
basicConstraints=CA:FALSE
subjectAltName=@v3_subject_alt_names
subjectKeyIdentifier = hash
extendedKeyUsage = serverAuth

[ v3_subject_alt_names ]
DNS.1 = $1
DNS.2 = *.$1
DNS.3 = $2
EOF

    openssl genrsa -out $PWD/.devres/pki/$1.key 4096
    openssl req -new -key $PWD/.devres/pki/$1.key -out $PWD/.devres/ca/csrs/$1.csr -config $PWD/.devres/ca/csrs/$1.csr.conf
}


function gen_ca_conf {
    echo "01" > "$PWD/.devres/ca/sd-connect.devca.srl"
    touch "$PWD/.devres/ca/sd-connect.devca.index.txt"
    cat > "$PWD/.devres/ca/sd-connect.devca.conf" <<EOF
[ ca ]
default_ca = sd-connect.devca

[ sd-connect.devca ]
serial = $PWD/.devres/ca/sd-connect.devca.srl
database = $PWD/.devres/ca/sd-connect.devca.index.txt
new_certs_dir = $PWD/.devres/pki
certificate = $PWD/.devres/ca/sd-connect.devca.crt
private_key = $PWD/.devres/ca/sd-connect.devca.key
default_md = sha256
default_days = 365
policy = sd-connect.devca.policy
copy_extensions = copy

[ sd-connect.devca.policy ]
countryName = match
stateOrProvinceName = supplied
organizationName = supplied
commonName = supplied
organizationalUnitName = optional

EOF
}


function gen_dev_ca {
    ensure_dev_res_dir
    gen_hosts
    gen_ceph_hosts

    pushd "$PWD/.devres/ca"
        cat > "ca.csr.conf" << EOF
[ req ]
default_bits = 4096
default_keyfile = $PWD/.devres/ca/sd-connect.devca.key
encrypt_key = no

default_md = sha256

prompt = no

utf8 = yes

distinguished_name = sd-connect.devca

req_extensions = v3_extensions

[ sd-connect.devca ]
C = FI
ST = Espoo
L = Espoo
O = CSC
OU = SDD
CN = sd-connect.devca
emailAddress = admin@ca.devenv

[ v3_extensions ]
basicConstraints=CA:TRUE
subjectAltName=@v3_subject_alt_names
subjectKeyIdentifier=hash
extendedKeyUsage=serverAuth

[ v3_subject_alt_names ]
DNS.1 = sd-connect.devca
EOF

        openssl genrsa -out sd-connect.devca.key 4096
        openssl req -x509 -new -nodes \
            -key sd-connect.devca.key \
            -sha256 \
            -days 1826 \
            -out sd-connect.devca.crt \
            -copy_extensions=copyall \
            -config ca.csr.conf
    popd

    gen_ca_conf

    gen_csr $DEV_UI_HOSTNAME $DEV_PROXY_IP
    gen_csr $DEV_CEPH_HOSTNAME $DEV_PROXY_IP
    gen_csr $DEV_KEYSTONE_HOSTNAME $DEV_PROXY_IP

    openssl ca \
        -batch \
        -config $PWD/.devres/ca/sd-connect.devca.conf \
        -out $PWD/.devres/pki/$DEV_UI_HOSTNAME.crt \
        -infiles $PWD/.devres/ca/csrs/$DEV_UI_HOSTNAME.csr
    openssl ca \
        -batch \
        -config $PWD/.devres/ca/sd-connect.devca.conf \
        -out $PWD/.devres/pki/$DEV_CEPH_HOSTNAME.crt \
        -infiles $PWD/.devres/ca/csrs/$DEV_CEPH_HOSTNAME.csr
    openssl ca \
        -batch \
        -config $PWD/.devres/ca/sd-connect.devca.conf \
        -out $PWD/.devres/pki/$DEV_KEYSTONE_HOSTNAME.crt \
        -infiles $PWD/.devres/ca/csrs/$DEV_KEYSTONE_HOSTNAME.csr
}


gen_dev_ca
