all: upload download

upload: build/upworker.js src/libupload.wasm

download: build/downworker.js src/libdownload.wasm

build/upworker.js: src/upinit.c src/streamingupload.c src/upcommon.c
	$(CC) $(CFLAGS) $(LDFLAGS) \
		-fsanitize=undefined \
		-s ERROR_ON_UNDEFINED_SYMBOLS=0 \
		-s WARN_UNALIGNED=1 \
		-s ALLOW_MEMORY_GROWTH \
		-s ASSERTIONS=1 \
		-g3 \
		-s TOTAL_MEMORY=268435456 \
		-s LLD_REPORT_UNDEFINED \
		-s FORCE_FILESYSTEM=1 \
		-s EXPORTED_RUNTIME_METHODS=ccall \
		-s EXPORTED_FUNCTIONS=_read_in_recv_keys_path,_wrap_chunk_content,_wrap_chunk_len,_rmrecv,_create_keypair,_create_session_key,_get_keypair_private_key,_create_crypt4gh_header,_free_chunk,_free_keypair,_encrypt_chunk,_libinit \
		-O3 \
		-o \
		$@ \
		$^ \
		-lcrypt4gh \
		-lc4gh-keys \
		-lssl \
		-lcrypto \
		-lsodium \
		--post-js build/upworker-post.js \
		--pre-js js/crypt-pre.js

build/downworker.js: src/upinit.c src/streamingdownload.c src/upcommon.c
	$(CC) $(CFLAGS) $(LDFLAGS) \
		-fsanitize=undefined \
		-s ERROR_ON_UNDEFINED_SYMBOLS=0 \
		-s WARN_UNALIGNED=1 \
		-s ALLOW_MEMORY_GROWTH \
		-s ASSERTIONS=1 \
		-g3 \
		-s TOTAL_MEMORY=268435456 \
		-s LLD_REPORT_UNDEFINED \
		-s FORCE_FILESYSTEM=1 \
		-s EXPORTED_RUNTIME_METHODS=ccall \
		-s EXPORTED_FUNCTIONS=_read_in_recv_keys_path,_wrap_chunk_content,_wrap_chunk_len,_rmrecv,_create_keypair,_get_session_key_from_header,_get_keypair_public_key,_free_chunk,_free_keypair,_decrypt_chunk,_libinit \
		-O3 \
		-o \
		$@ \
		$^ \
		-lcrypt4gh \
		-lc4gh-keys \
		-lssl \
		-lcrypto \
		-lsodium \
		--post-js build/downworker-post.js \
		--pre-js js/crypt-pre.js


clean:
	rm -rf build
