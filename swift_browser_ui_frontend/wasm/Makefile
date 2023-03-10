all: src/libupload.js src/libupload.wasm

src/libupload.js: src/upinit.c src/streamingupload.c src/upcommon.c src/streamingdownload.c
	$(CC) $(CFLAGS) $(LDFLAGS) -fsanitize=undefined -sERROR_ON_UNDEFINED_SYMBOLS=0 -sWARN_UNALIGNED=1 -sALLOW_MEMORY_GROWTH -sASSERTIONS=1 -g3 -sTOTAL_MEMORY=268435456 -sEXPORTED_FUNCTIONS='["_allocate_chunk","_free_chunk","_wrap_chunk_len","_wrap_chunk_content","_open_session","_open_session_eph","_open_session_enc","_wrap_crypt4gh_header","_encrypt_chunk","_clean_session","_rmrf","_open_decrypt_session","_get_session_public_key","_get_session_private_key","_get_session_key","_open_crypt4gh_header","_decrypt_chunk", "_libinit"]' -s LLD_REPORT_UNDEFINED -s FORCE_FILESYSTEM=1 -s EXPORTED_RUNTIME_METHODS='["ccall"]' -O3 -o $@ $^ -lcrypt4gh -lc4gh-keys -lssl -lcrypto -lsodium --post-js js/crypt-post.js --pre-js js/crypt-pre.js

clean:
	rm -f src/libupload.wasm src/libupload.js
