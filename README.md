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

Readmes on the additional APIs for container sharing, access requests, and
better upload and download functionality are in their separate files.

* Container sharing – `README-sharing.md`
* Container access requests – `README-request.md`
* Additional upload and download functionality `README-runner.md`

### Requirements

Python 3.6+ required (recommended 3.7+)

The dependencies mentioned in `requirements.txt` and a suitable storage backend
supporting usage via Openstack Object Storage API. (e.g. Ceph RGW, Openstack Swift)

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
cd swift_browser_ui
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

### License

``swift-browser-ui`` and all it sources are released under *MIT License*.
