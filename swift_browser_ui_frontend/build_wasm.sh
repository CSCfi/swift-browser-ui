#!/usr/bin/env sh

set -e

SCRIPT="$(realpath $0)"
SCRIPT_ROOT=$(dirname "$SCRIPT")
WASM_ROOT="${SCRIPT_ROOT}"/wasm

buildWasm() {
    mkdir "${WASM_ROOT}/build"
    (
        cd $SCRIPT_ROOT
        npx webpack --config "${WASM_ROOT}/wasm-webpack.config.js"
        cd $WASM_ROOT
    )

    if [ "$1" = "docker" ]; then
        docker run --rm -it --mount type=bind,source="${WASM_ROOT}",target=/src/ ghcr.io/cscfi/docker-emscripten-crypt4gh all
    elif [ "$1" = "emsdk" ]; then
        /emsdk/upstream/emscripten/emmake make all
    fi
}

if [ -x "/emsdk/emsdk" ]; then
    echo "Running in an environment with natively supported emsdk. Building WASM contents using that."
    export EMCC_CFLAGS="-I/emsdk/upstream/include -L/emsdk/upstream/lib -sINITIAL_MEMORY=26214400"
    export EMCC_FORCE_STDLIBS="libc"

    cd $WASM_ROOT

    /emsdk/upstream/emscripten/emmake make clean
    buildWasm "emsdk"

    cd $SCRIPT_ROOT
else
    echo "emsdk was not configured, checking for docker"
    [ ! -x "$(command -v docker)" ] && echo "Docker is used to build the javascript WebAssembly dependencies, but it's not installed." && exit;
    if ! docker version > /dev/null 2>&1; then echo "Docker is installed, but it seems like there's an error."; exit 1; fi

    docker run --rm -it --mount type=bind,source="${WASM_ROOT}",target=/src/ ghcr.io/cscfi/docker-emscripten-crypt4gh clean
    buildWasm "docker"
fi

cp "${WASM_ROOT}/build/upworker.js" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/downworker.js" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/upworker-post.js.map" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/downworker-post.js.map" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/upworker.wasm" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/downworker.wasm" "${SCRIPT_ROOT}/public/"

# Copy over the S3 compatible versions as well
cp "${WASM_ROOT}/build/s3upworker.js" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/s3upworker.wasm" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/crypt-post-s3upload.js.map" "${SCRIPT_ROOT}/public/"

cp "${WASM_ROOT}/build/s3downworker.js" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/s3downworker.wasm" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/crypt-post-s3download.js.map" "${SCRIPT_ROOT}/public/"

cp "${WASM_ROOT}/build/s3headerworker.js" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/s3headerworker.wasm" "${SCRIPT_ROOT}/public/"
cp "${WASM_ROOT}/build/crypt-post-headers.js.map" "${SCRIPT_ROOT}/public/"
