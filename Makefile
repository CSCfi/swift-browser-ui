SHELL := /bin/bash

dev:
	echo "Not yet implemented"

dev-ff: dev-ca
	mkdir -p $(PWD)/.devres/profiles/ff

dev-chromium: dev-ca
	mkdir -p $(PWD)/.devres/profiles/chromium

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
