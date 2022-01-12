all: src/libupload.js

src/libupload.js: src/upinit.c src/upload.c
	$(CC) $(CFLAGS) $(LDFLAGS) -s EXPORTED_FUNCTIONS='["_encrypt_folder","_encrypt_folder_ephemeral"]' -s LLD_REPORT_UNDEFINED -s FORCE_FILESYSTEM=1 -s EXPORTED_RUNTIME_METHODS='["ccall"]' -O3 -o $@ $^ -lcrypt4gh -lc4gh-keys -lssl -lcrypto -lsodium -lidbfs.js
