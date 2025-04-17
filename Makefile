SHELL := /bin/bash

dev:
	echo "Not yet implemented"

dev-ff: dev-ca
	mkdir -p .devres/ssh
	ssh-keygen -t ed25519 -f .devres/ssh/ff-dev -q -N ""
	docker build -t dev-ff -f devproxy/Dockerfile-ff .
	docker run --rm -p 3022:22 -d --name development-ca-firefox dev-ff
	ssh -i .devres/ssh/ff-dev -XC -p 3022 root@localhost firefox
	docker rm -f development-ca-firefox

dev-chromium: dev-ca
	mkdir -p .devres/ssh
	ssh-keygen -t ed25519 -f .devres/ssh/chrome-dev -q -N ""
	docker build -t dev-chrome -f devproxy/Dockerfile-chrome .
	docker run --rm -p 3122:22 -d --name development-ca-chrome dev-chrome
	ssh -i .devres/ssh/chrome-dev -XC -p 3122 root@localhost chromium --no-sandbox
	docker rm -f development-ca-chrome

dev-ca:
	mkdir -p $(PWD)/.devres/ca
	if [[ -z $$(ls $(PWD)/.devres/ca) ]]; then \
		$(PWD)/scripts/gen_ca.sh; \
	fi

ceph-up:
	$(MAKE) -C submodules/local-single-host-ceph up || make ceph-bootstrap

ceph-bootstrap:
	$(MAKE) -C submodules/local-single-host-ceph all

ceph-down:
	$(MAKE) -C submodules/local-single-host-ceph down

ceph-clean:
	$(MAKE) -C submodules/local-single-host-ceph clean-full

ceph-attach:
	$(MAKE) -C submodules/local-single-host-ceph attach-vm

ceph-install-ssl:
	SD_CONNECT_REPO_LOCATION="$(PWD)" $(MAKE) -C submodules/local-single-host-ceph install-ssl
