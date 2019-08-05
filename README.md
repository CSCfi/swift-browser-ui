## swift-browser-ui

[![Build Status](https://travis-ci.com/CSCfi/swift-browser-ui.svg?branch=master)](https://travis-ci.com/CSCfi/swift-browser-ui)
[![Coverage Status](https://coveralls.io/repos/github/CSCfi/swift-browser-ui/badge.svg?branch=master)](https://coveralls.io/github/CSCfi/swift-browser-ui?branch=master)
[![Documentation Status](https://readthedocs.org/projects/swift-browser-ui/badge/?version=latest)](https://swift-browser-ui.readthedocs.io/en/latest/?badge=latest)

### Description

A web frontend for browsing and downloading objects saved in [SWIFT](https://docs.openstack.org/swift/latest/)
compliant object storage, supporting SSO with SAML2 federated authentication.

Project documentation is hosted on readthedocs: https://swift-browser-ui.rtfd.io

### Requirements

Python 3.6+ required

The dependencies mentioned in `requirements.txt` and an account that has access
rights to CSC Pouta platform, and is taking part to at least one project as
object stoarge is project specific.

### Usage

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
git clone git@gitlab.csc.fi:CSCCSDP/swift_browser_ui.git
cd swift_browser_ui
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
