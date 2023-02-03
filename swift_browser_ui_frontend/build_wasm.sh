#!/usr/bin/env bash

set -e

SCRIPT="$(realpath $0)"
SCRIPT_ROOT=$(dirname "$SCRIPT")

WASM_ROOT="${SCRIPT_ROOT}"/wasm/

docker run --rm -it --mount type=bind,source="${WASM_ROOT}",target=/src/ ghcr.io/cscfi/docker-emscripten-crypt4gh clean
docker run --rm -it --mount type=bind,source="${WASM_ROOT}",target=/src/ ghcr.io/cscfi/docker-emscripten-crypt4gh all
cp "${WASM_ROOT}"/src/libupload* "${SCRIPT_ROOT}"/public
