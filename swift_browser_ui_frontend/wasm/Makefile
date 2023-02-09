all: src/libupload.js src/libupload.wasm

src/libupload.js: src/upinit.c src/upload.c src/streamingupload.c src/upcommon.c src/streamingdownload.c
	$(CC) $(CFLAGS) $(LDFLAGS) -sALLOW_MEMORY_GROWTH -s ASSERTIONS=1 -s EXPORTED_FUNCTIONS='["_allocate_chunk","_free_chunk","_wrap_chunk_len","_wrap_chunk_content","_encrypt_folder","_encrypt_folder_ephemeral","_open_session","_open_session_eph","_open_session_enc","_wrap_crypt4gh_header","_encrypt_chunk","_clean_session","_rmrf","_open_decrypt_session","_get_session_public_key","_get_session_private_key","_get_session_key","_open_crypt4gh_header","_decrypt_chunk"]' -s LLD_REPORT_UNDEFINED -s FORCE_FILESYSTEM=1 -s EXPORTED_RUNTIME_METHODS='["ccall"]' -O3 -o $@ $^ -lcrypt4gh -lc4gh-keys -lssl -lcrypto -lsodium --post-js js/crypt-post.js --pre-js js/crypt-pre.js

clean:
	rm -f src/libupload.wasm src/libupload.js
