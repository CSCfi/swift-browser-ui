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

Getting started:

```
git clone git@gitlab.csc.fi:CSCCSDP/s3-object-browser.git
cd s3-object-browser
pip install -r requirements.txt
python -m s3browser.server
```

The current frontend can be found at: `127.0.0.1:8080`.
