SHELL := /bin/bash

# Whitespace separated list of dependency:version, eg. "python:3.12", used for automatic dependency checking
# Dependencies without version are also supported, eg. "docker"
REQ_CMDS := node:22 npm:9 pnpm:9 python:3.12 docker

dev-up:
	# make ceph-up
	CURRENT_UID=$(id -u):$(id -g) docker compose -f docker-compose-dev.yml up
	# honcho start

dev-all:
	@echo Checking dependencies
	make check-deps
	@echo Building the whole development environment
	make ceph-up
	make dev-ca
	make volumes
	docker compose -f docker-compose-dev.yml build
	CURRENT_UID=$(id -u):$(id -g) docker compose -f docker-compose-dev.yml up
	# honcho start

dev-down:
	docker compose -f docker-compose-dev.yml down
	# make ceph-down

dev-ff: dev-ca
	ssh -o StrictHostKeyChecking=no -i .devres/ssh/ff-dev -XC -p 3022 root@localhost firefox --width 1920 --height 1080 https://sd-connect.devenv

dev-chromium: dev-ca
	ssh -o StrictHostKeyChecking=no -i .devres/ssh/chrome-dev -XC -p 3122 chromeuser@localhost chromium --no-sandbox --window-size=1920,1080 --window-position=0,0 https://sd-connect.devenv

dev-ca:
	mkdir -p $(CURDIR)/.devres/ca
	mkdir -p $(CURDIR)/.devres/ssh
	if [[ -z $$(ls $(CURDIR)/.devres/ca) ]]; then \
		$(CURDIR)/scripts/gen_ca.sh; \
	fi
	if [[ -z $$(ls $(CURDIR)/.devres/ssh) ]]; then \
		ssh-keygen -t ed25519 -f .devres/ssh/ff-dev -q -N ""; \
		ssh-keygen -t ed25519 -f .devres/ssh/chrome-dev -q -N ""; \
	fi

dev-ca-clean:
	rm -rf .devres
	ssh-keygen -f "$(HOME)/.ssh/known_hosts" -R '[localhost]:3022' ; ssh-keygen -f "$(HOME)/.ssh/known_hosts" -R '[localhost]:3122'

dev-docker-build:
	docker compose -f docker-compose-dev.yml build

dev-docker-up:
	make volumes
	CURRENT_UID=$(id -u):$(id -g) docker compose -f docker-compose-dev.yml up

dev-docker-down:
	docker compose -f docker-compose-dev.yml down

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
	SD_CONNECT_REPO_LOCATION="$(CURDIR)" $(MAKE) -C submodules/local-single-host-ceph install-ssl

test-data:
	dd if=/dev/urandom of=.docker-volumes/test-data/test-data-1.bin bs=1M count=128
	dd if=/dev/urandom of=.docker-volumes/test-data/test-data-2.bin bs=1M count=256
	dd if=/dev/urandom of=.docker-volumes/test-data/test-data-3.bin bs=1M count=512
	dd if=/dev/urandom of=.docker-volumes/test-data/test-data-4.bin bs=1M count=768

volumes:
	mkdir -p .docker-volumes/test-data
	# Create volume mounts for firefox
	mkdir -p .docker-volumes/config-ff
	mkdir -p .docker-volumes/cache-ff
	mkdir -p .docker-volumes/local-ff
	mkdir -p .docker-volumes/mozilla-ff
	# Create volume mounts for chrome
	mkdir -p .docker-volumes/config-chrome
	mkdir -p .docker-volumes/cache-chrome
	mkdir -p .docker-volumes/local-chrome
	# We need to use the chromeuser uid for the chrome volumes to preserve rights
	sudo chown -R 1111:1111 .docker-volumes/config-chrome
	sudo chown -R 1111:1111 .docker-volumes/cache-chrome
	sudo chown -R 1111:1111 .docker-volumes/local-chrome

check-deps:
	@for dep in $(REQ_CMDS); do \
		cmd="$${dep%%:*}"; \
		min="$${dep#*:}"; \
		if ! command -v $$cmd >/dev/null 2>&1; then \
			echo "Error: $$cmd is not installed or not in PATH"; \
			exit 1; \
		fi; \
		if [ "$$dep" = "$$cmd" ]; then \
			continue; \
		fi; \
		version="$$($$cmd --version 2>/dev/null | sed -E 's/[^0-9]*([0-9]+(\.[0-9]+)?).*/\1/')"; \
		if [ -z "$$version" ]; then \
			echo "Error: could not determine version for $$cmd"; \
			exit 1; \
		fi; \
		printf "%s\n%s\n" "$$min" "$$version" | sort -V -C || { \
			echo "Error: $$cmd must be >= $$min (currently $$version)"; \
			exit 1; \
		}; \
	done
	$(MAKE) -C submodules/local-single-host-ceph check-deps

clean-browsers:
	sudo rm -rf .docker-volumes

clean:
	make dev-ca-clean
	make ceph-clean
