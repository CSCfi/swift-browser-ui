#!/usr/bin/env sh

set -e

[[ ! -x "$(command -v docker)" ]] && echo "Docker is used to build the javascript WebAssembly dependencies, but it's not installed." && exit;
if ! docker version > /dev/null 2>&1; then echo "Docker is installed, but it seems like there's an error."; exit 1; fi

SCRIPT="$(realpath $0)"
SCRIPT_ROOT=$(dirname "$SCRIPT")
WASM_ROOT="${SCRIPT_ROOT}"/wasm/

docker run --rm -it --mount type=bind,source="${WASM_ROOT}",target=/src/ ghcr.io/cscfi/docker-emscripten-crypt4gh clean
docker run --rm -it --mount type=bind,source="${WASM_ROOT}",target=/src/ ghcr.io/cscfi/docker-emscripten-crypt4gh all
cp "${WASM_ROOT}"/src/libupload* "${SCRIPT_ROOT}"/public/
cp "${WASM_ROOT}"/src/libupload* "${SCRIPT_ROOT}"/dist/
