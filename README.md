## swift-browser-ui

![Python Unit Tests](https://github.com/CSCfi/swift-browser-ui/workflows/Python%20Unit%20Tests/badge.svg)
![Javascript ESLint check](https://github.com/CSCfi/swift-browser-ui/workflows/Javascript%20ESLint%20check/badge.svg)
![Python style check](https://github.com/CSCfi/swift-browser-ui/workflows/Python%20style%20check/badge.svg)

A web frontend for browsing and managing objects saved using S3 compatible object storage.
Currently developed and tested using Openstack identity API and Ceph object storage.

Project documentation is hosted as a part of the source code.

Information on the additional APIs for bucket sharing and encryption resource management
are in their separate files.

* [Bucket sharing](README-sharing.md)
* [Encryption resource APIs](README-runner.md)

### 💻 Development
<details open><summary>Click to expand</summary>

#### Prerequisites

Bare minimum

* Python 3.12+ required (pyenv recommended for installation)
* Node version 22+ required, 24 recommended (nvm recommended for installation)
* pnpm 9+ (`npm install -g pnpm@9`)
* working docker
* sudo (due to docker access rights we haven't bothered to fix)
* git
* ssh (client)
* dev python dependencies (`pip install .[dev]`)

Testing
* test python dependencies (`pip install .[test]`)
* ui testing python dependencies (`pip install . .[ui_test]`)

Local ceph

* libvirt, virsh + compatible hardware virtualization backend (e.g. kvm or hvf)
* 60 GiB available disk space
* 8 GiB RAM to spare (32 GiB on the laptop)

Default installation (with local Ceph):

```bash
git clone --recurse-submodules ssh://git@gitlab.ci.csc.fi:10022/sds-dev/sd-connect/swift-browser-ui.git
# OR from the public repo
git clone --recurse-submodules https://github.com/cscfi/swift-browser-ui

cd swift-browser-ui

# Environment checks, not needed after it's been run once
pyenv install 3.12 \
	&& pyenv virtualenv 3.12 sd-connect-dev \

make check-deps \
	&& pyenv activate sd-connect-dev \
	&& pushd swift_browser_ui_frontend ; pnpm i ; popd \
	&& cp .github/config/.env.test .env \
	&& make
```

> TODO: Reduced installation (without local Ceph):

#### Running

In the repository root folder:
```
make dev-up
```

If the ceph environment is already running, or when using an external S3 storage
for testing, you can get by with just
```
make dev-docker-up
```

#### OIDC login provider configuration

> TODO: update to take the docker environment into account

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

#### Pre-commit
In your virtual environment, check that the required dependencies have been installed
and enable pre-commit.

```
pyenv activate sd-connect-dev
pip install -Ue .[test,dev]
pre-commit install
```
</details>

### 🛠️  Contributing

<details><summary>Click to expand</summary>

Development team members should check internal [contributing guidelines for Gitlab](https://gitlab.ci.csc.fi/groups/sds-dev/-/wikis/Guides/Contributing).

If you are not part of CSC and our development team, your help is nevertheless very welcome. Please see [contributing guidelines for Github](CONTRIBUTING.md).

</details>

### 🧪 Testing

<details><summary>Click to expand</summary>

#### Backend
The backend `python` tests can be run with `tox`. Start the mock server in one terminal, and run tox in another.

```bash
pyenv activate sd-connect-dev
pip install -Ue .[test,dev]
tox
```

#### TODO: frontend

#### WebAssembly C Code Unit Tests
C code is tested using a unit tests collection built using `ceedling`. They can be ran by
navigating to the `swift_browser_ui_frontend/wasm` directory and running the `ceedling` command.
You'll have to install `ceedling` first, which can be found [here](https://www.throwtheswitch.org/ceedling)

</details>

### 🚀 Deployment

<details><summary>Click to expand</summary>

Deployment can be done using the `Dockerfile`s in the repository.

TODO: add generic deployment instructions.

</details>

### 📜 License

<details><summary>Click to expand</summary>

Software is released under `MIT`, see [LICENSE](LICENSE).

</details>
