# s3-object-browser

### Description
A web frontend for browsing and downloading objects saved in s3 or swift
compliant object storage, supporting SSO with SAML2 federated authentication.

### Requirements
The dependencies mentioned in requirements.txt and an account that has access
rights to CSC Pouta platform, and is taking part to at least one project as
object stoarge is project specific.

### Usage
Currently run by hand in the Python interpreter:  
```
from s3browser.server import run_server_insecure, servinit
run_server_insecure(servinit())
```
The current frontend can be found in the location 127.0.0.1:8080
