all: src/libupload.js

src/libupload.js: src/upinit.c src/upload.c
	$(CC) $(CFLAGS) $(LDFLAGS) -s LLD_REPORT_UNDEFINED -s FORCE_FILESYSTEM=1 -O3 -o $@ $^ -lcrypt4gh -lc4gh-keys -lssl -lcrypto -lsodium -lidbfs.js
