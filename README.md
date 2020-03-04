### swift-upload-runner – resumable browser file upload and replication
`swift-upload-runner` makes it possible to properly batch upload from browser
into object storage backends using Openstack Swift API. It also makes possible
proper container uploads without plaintext passwords or tokens, to prevent
token expiration.

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
