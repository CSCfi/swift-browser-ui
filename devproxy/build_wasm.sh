#!/usr/bin/env bash


EMCC_CFLAGS="-I/emsdk/upstream/include -L/emsdk/upstream/lib" EMCC_FORCE_STDLIBS=libc emmake make $1
