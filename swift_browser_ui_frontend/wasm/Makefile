all: src/libupload.js

src/libupload.js: src/upinit.c src/upload.c src/streamingupload.c
	$(CC) $(CFLAGS) $(LDFLAGS) -s ASSERTIONS=1 -s EXPORTED_FUNCTIONS='["_allocate_chunk","_free_chunk","_wrap_chunk_len","_wrap_chunk_content","_encrypt_folder","_encrypt_folder_ephemeral","_open_session","_open_session_eph","_wrap_crypt4gh_header","_encrypt_chunk","_clean_session","_rmrf"]' -s LLD_REPORT_UNDEFINED -s FORCE_FILESYSTEM=1 -s EXPORTED_RUNTIME_METHODS='["ccall"]' -O3 -o $@ $^ -lcrypt4gh -lc4gh-keys -lssl -lcrypto -lsodium -lidbfs.js --post-js js/crypt-post.js
