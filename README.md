## s3-object-browser

Python 3.6+ required

### Description

A web frontend for browsing and downloading objects saved in s3 or swift
compliant object storage, supporting SSO with SAML2 federated authentication.

### Requirements

The dependencies mentioned in requirements.txt and an account that has access
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
export BROWSER_START_SWIFT_ENDPOINT_URL="https://object-storage-url.example.com:443/swift"
export BROWSER_START_STATIC_DIRECTORY="s3browser_frontend"
export BROWSER_START_PORT="8080"'\
|tee -a envs.sh && chmod u+x envs.sh
```

Getting started:
```
git clone git@gitlab.csc.fi:CSCCSDP/s3-object-browser.git
cd s3-object-browser
pip install -r requirements.txt
. path_to_envs_file && python -m s3browser.shell start
```

Additional options can be found with
```
python -m s3browser.shell --help
python -m s3browser.shell start --help
```

The current frontend can be found at: `127.0.0.1:8080`.
