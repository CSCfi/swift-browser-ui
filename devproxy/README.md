### Development TLS proxy
This folder contains a development TLS proxy to make hosting the service
with HTTPS enabled more simple. It contains a configuration file for
Nginx and a Dockerfile for building it.

### Building
You will need the certificate files to be used with the proxy. These
should be named `swiftui-proxy.crt` for the certificate file, and
`swiftui-proxy.key` for the key. Ensure these files are present in
this folder before starting the build.

In order to test the upload functionality these certificates need
to be signed by an authority trusted by your browser, but nothing
is preventing you from using your own certificate authority as
long as it has been added to whatever browser you're testing with.

Change localhost in `nginx.conf` if you want to e.g. specify an IP
address.

```
$ docker build -f Dockerfile-nginx -t swiftui-dev-proxy .
```

### Wasm dependency install
A dockerfile for building an emsdk container with required dependencies
is provided in `Dockerfile-emsdk-deps`. It can be used by
```
$ docker buildx build -f Dockerfile-emsdk-deps -t wasmbuilder .
```

### Usage
The development proxy is mainly used via honcho and the `Procfile`
provided for development.
