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
- A suitable storage backend supporting usage via Openstack Object Storage API. (e.g. Ceph RGW, Openstack Swift)
- PosgreSQL
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
npm install
npm run build
cd ..
pip install -r requirements.txt
pip install .
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
They depend on a redis instance for session cache, postgres database for the sharing and 
request functionality, and the object storage backend.
You will also need docker with buildkit to build the keystone-swift docker image.

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
npm --prefix swift_browser_ui_frontend install
npm --prefix swift_browser_ui_frontend run build
```

Install python dependencies, optionally in a virtual environemnt.

```bash
python3 -m venv venv --prompt swiftui  # Optional step, creates python virtual environment
source venv/bin/activate  # activates virtual environment
pip install -Ue .
pip install honcho  # to run the Procfile
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

Now you should be able to access the development server at localhost:8081. The login and password are `swift`, and `veryfast`, respectivelly.

This configuration has both frontend and backend servers running with code reloading features, meaning that after code changes the servers reload.

The `keystone-swift` image comes with a script to generate data in the object storage server. You can use like this:
```bash
docker exec keystone-swift generate_data.py --keystone --username swift --password veryfast --containers 15
docker exec keystone-swift generate_data.py --keystone --username swift --password veryfast --project "swift-project"
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
The frontend tests are run with `cypress`, and you will need the full backend running, as shown above, as well as using a specific command for generating data.

The `keystone-swift` image comes with a script to generate data in the object storage server. With the services running, run these commands:
```bash
docker exec keystone-swift generate_data.py --keystone --username swift --password veryfast --containers 15
docker exec keystone-swift generate_data.py --keystone --username swift --password veryfast --project "swift-project"
```

After following the development steps above, `cypress` should already be installed.

    cd swift_browser_ui_frontend

You can run the tests in headless mode
  
    npx cypress run

Or you can use the inteactive version

    npx cypress open


### License

``swift-browser-ui`` and all it sources are released under *MIT License*.
