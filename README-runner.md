### swift-upload-runner – better browser file upload and download for swift-browser-ui

`swift-upload-runner` makes it possible to properly batch upload from browser
into object storage backends using Openstack Swift API. It will also make possible
proper container uploads without plaintext passwords or tokens, to prevent
token expiration.

Additionally, the runner contains functionality for downloading whole containers
as an archive without intermediary storage, as well as proxying downloads from
shared containers, i.e. containers where the project has access via an ACL entry.

### Installation
`pip install git+https://github.com/cscfi/swift-upload-runner.git`

### Running

#### Environment variables
The service requires following environment variables:

* OS_AUTH_URL for openstack authentication URL
* SWIFT_UI_API_AUTH_TOKENS for accepted API keys

The following environment variables are optional:

* SWIFT_UPLOAD_RUNNER_PORT for the port on which the server runs
* SWIFT_UPLOAD_RUNNER_PROXY_Q_SIZE for buffered chunk amount
* SWIFT_UPLOAD_RUNNER_MAX_SESSION_CONNECTIONS for max connections per session

#### Python
By default the service runs on port `9092` and can be invoked with the command
`swift-upload-runner`
