## swift-browser-ui

![Python Unit Tests](https://github.com/CSCfi/swift-browser-ui/workflows/Python%20Unit%20Tests/badge.svg)
![Javascript ESLint check](https://github.com/CSCfi/swift-browser-ui/workflows/Javascript%20ESLint%20check/badge.svg)
![Python style check](https://github.com/CSCfi/swift-browser-ui/workflows/Python%20style%20check/badge.svg)
![Chrome UI check](https://github.com/CSCfi/swift-browser-ui/workflows/Chrome%20UI%20check/badge.svg)
![Firefox UI check](https://github.com/CSCfi/swift-browser-ui/workflows/Firefox%20UI%20check/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/CSCfi/swift-browser-ui/badge.svg?branch=HEAD)](https://coveralls.io/github/CSCfi/swift-browser-ui?branch=HEAD)
[![Documentation Status](https://readthedocs.org/projects/swift-browser-ui/badge/?version=latest)](https://swift-browser-ui.readthedocs.io/en/latest/?badge=latest)



### Description

A web frontend for browsing and downloading objects saved in [SWIFT](https://docs.openstack.org/swift/latest/)
compliant object storage, supporting SSO with SAML2 federated authentication.

Project documentation is hosted on readthedocs: https://swift-browser-ui.rtfd.io

Information on the additional APIs for container sharing, access requests, and
better upload and download functionality are in their separate files.

* [Container sharing](README-sharing.md)
* [Container access requests](README-request.md)
* [Additional upload and download functionality](README-runner.md)

### Requirements

Python 3.8+ required.

- The dependencies mentioned in `requirements.txt`.
- A suitable storage backend supporting usage via OpenStack Object Storage API. (e.g. Ceph RGW, OpenStack Swift)
- PostgreSQL
- Redis

### Usage – UI

At the current state the program configs can be specified either via environment
variables or command line arguments. These usage directions assume envvars to be used.

Creating environment variable file for stand-alone use (no TLS proxy):
```
# Replace the example URLs with correct ones
echo '
export BROWSER_START_AUTH_ENDPOINT_URL="https://keystone-url.example.com:5001/v3"
export BROWSER_START_PORT="8080"'\
|tee -a envs.sh && chmod u+x envs.sh
```

Getting started:
```
git clone git@github.com:CSCfi/swift-browser-ui.git
cd swift-browser-ui
cd swift_browser_ui_frontend
npm install -g pnpm@7
pnpm install
pnpm run build
cd ..
pip install -r requirements.txt
pip install .[]
```

After install there should be `swift-browser-ui` command available:
```
➜ swift-browser-ui --help
Usage: swift-browser-ui [OPTIONS] COMMAND [ARGS]...

  Command line interface for managing swift-browser-ui.

Options:
  --version       Show the version and exit.
  -v, --verbose   Increase program verbosity.
  -D, --debug     Enable debug level logging.
  --logfile TEXT  Write program logs to a file.
  --help          Show this message and exit.

Commands:
  start    Start the browser backend and server
```

In order to start the server use `swift-browser-ui start`.

Additional options can be found with
```
swift-browser-ui --help
swift-browser-ui start --help
```

The current frontend can be found at: `127.0.0.1:8080`.

### Development
swift-browser-ui is composed of 4 components: `request`, `sharing`, `ui`, and `upload`.
All of them must be run to have access to all features.
They depend on a Redis instance for session cache, Postgres database for the sharing and 
request functionality, and the object storage backend.
You will also need docker with Buildkit to build the keystone-swift docker image.

To start all required services, you can use the `docker-compose` files from https://github.com/CSCfi/swift-ui-deployment,
or the provided `Procfile`, as shown bellow.

Please, read and adhere to the [CONTRIBUTING guidelines](CONTRIBUTING.md) for submitting changes.

#### Getting started:
```bash
git clone -b devel git@github.com:CSCfi/swift-browser-ui.git
cd swift-browser-ui
```
Install frontend dependencies, and build (without encryption or OIDC enabled).

```bash
pnpm --prefix swift_browser_ui_frontend install
pnpm --prefix swift_browser_ui_frontend run build
```

Install python dependencies, optionally in a virtual environment.

```bash
python3 -m venv venv --prompt swiftui  # Optional step, creates python virtual environment
source venv/bin/activate  # activates virtual environment
pip install -Ue .[docs,test,dev]
```

Set up the environment variables

```bash
cp .github/config/.env.test .env  # Make any changes you need to the file
```

Open another terminal, and build the `keystone-swift` image

```bash
git clone git@github.com:CSCfi/docker-keystone-swift.git
cd docker-keystone-swift
docker buildx build -t keystone-swift .
```

Start the servers

```bash
honcho start
```

Now you should be able to access the development server at localhost:8081. The login and password are `swift`, and `veryfast`, respectively.

This configuration has both frontend and backend servers running with code reloading features, meaning that after code changes the servers reload.

##### Trusted TLS
Additionally, when testing with the encrypted upload features, browser
features are used that **require** a trusted TLS connection. This can
be achieved by using a development proxy server that can be built from
files in the `devproxy` folder. [The proxy has it's own instructions for building.](devproxy/README.md)

This guide assumes you're using `devenv` as the domain name. Replace this
with the domain you're certificate sings, and if necessary, add it to
`/etc/hosts` so it's resolvable both in docker, and locally.

Additional setup is required in your environment file. You'll need to 
configure the following keys to point to whatever hostname will be used
to access the service. Additionally you should allow all hosts, assuming
your machine is in a secure network when developing. In case you trust
your network and want as easy of a setup as possible, you can use all to
greenlight all hosts for access.

```
SWIFT_UI_FRONTEND_ALLOW_HOSTS=devenv
SWIFT_UI_TLS_PORT=8443
SWIFT_UI_TLS_HOST=hostname
```

Additionally you'll need to configure the endpoints to be correct, so that
the backend APIs work as intended.
```
BROWSER_START_SHARING_ENDPOINT_URL=https://devenv:9443
BROWSER_START_SHARING_INT_ENDPOINT_URL=http://localhost:9090
BROWSER_START_REQUEST_ENDPOINT_URL=https://devenv:10443
BROWSER_START_REQUEST_INT_ENDPOINT_URL=http://localhost:9091
BROWSER_START_RUNNER_ENDPOINT=http://localhost:9092
BROWSER_START_RUNNER_EXT_ENDPOINT=https://devenv:11443
```

If your Docker network does not match the default, you'll need to change the
network configuration to make the proxy aware of the backend services. The
environment network defaults to the default Docker network, which is:
```
DOCKER_NETWORK_SEGMENT=172.17.0.0/24
DOCKER_NETWORK_GATEWAY=172.17.0.1
```

After this, comment out the commands to run without trusted TLS in the
`Procfile`, and uncomment the commands to run with trusted TLS.

You should now be able to run the service with trusted TLS by running
```bash
honcho start
```

##### OIDC login provider

To run with OIDC support, set the `OIDC_` environment variables in the `.env` file and restart the services. You'll also need to build the frontend again:

    OIDC_ENABLED=True pnpm --prefix swift_browser_ui_frontend run build

CSC OIDC provider's certificate should be added to `certifi`'s certificate store:
```bash
cd swift-browser-ui
source venv/bin/activate

curl -sLo oidc-cert.pem https://crt.sh/?d=2475254782
cert_path=$(python -c "import certifi;print(certifi.where())")
cat oidc-cert.pem >> ${cert_path}
rm oidc-cert.pem
```

#### Encrypted uploads
Encrypted uploads require that Hashicorp Vault is running and configured to use the `crypt4gh` transit encryption plugin.

With that done, set the policies and permissions to an account, so that they can use it, and set the account token to
the environment variables `VAULT_ROLE`, `VAULT_SECRET`, and `VAULT_URL`.

During development, you can configure and run Vault locally

Follow instructions for starting vault local dev server https://gitlab.ci.csc.fi/sds-dev/c4gh-transit#usage

##### Setting up API authentication
Enable `approle` module
```
vault auth enable approle
```

Create [policy](.github/config/vault_policy.hcl) to give access rights to the role
```
vault policy write swiftbrowser .github/config/vault_policy.hcl
```

Create a new role
```
vault write auth/approle/role/swiftbrowser \
    secret_id_ttl=0 \
    secret_id_num_uses=0 \
    token_ttl=5m \
    token_max_ttl=5m \
    token_num_uses=0 \
    token_policies=swiftbrowser \
    role_id=swiftbrowserui
```

Get role and secret (= username and password), set them to the environment variables mentioned above
```
vault read auth/approle/role/swiftbrowser/role-id
vault write -f auth/approle/role/swiftbrowser/custom-secret-id secret_id=swiftui
```

### Testing

#### Backend
The backend `python` tests can be run with `tox`. Start the mock server in one terminal, and run tox in another.

```bash
cd swift-browser-ui
source venv/bin/activate
python tests/ui_unit/mock_server.py
```

and in another terminal

```bash
cd swift-browser-ui
source venv/bin/activate
pip install tox
tox
```

#### Frontend
The frontend tests are run with `cypress`, and you will need

1. Full backend running, as shown above
2. Building the `wasm` code for encryption support
3. using a specific command for generating data

The wasm code is built automatically when using `npm` commands. It can also be triggered by running `npm run build-wasm`

> NOTE: Remember that the encrypted upload features cannot be used without
> having trusted TLS set up on all backend services.

The `keystone-swift` image comes with a script to generate data in the object storage server. With the services running, run these commands:
```bash
docker exec keystone-swift generate_data.py --keystone --username swift --password veryfast --containers 15
docker exec keystone-swift generate_data.py --keystone --username swift --password veryfast --project "swift-project"
```

After following the development steps above, `cypress` should already be installed.

    cd swift_browser_ui_frontend

You can run the tests in headless mode
  
    npx cypress run

Or you can use the interactive version

    npx cypress open

It's possible to set the host to run against by using the environment variable `CYPRESS_BASE_URL`, so that it may run against the development frontend server, for e.g.

    CYPRESS_BASE_URL=http://localhost:8081 npx cypress open

### License

``swift-browser-ui`` and all it sources are released under *MIT License*.
