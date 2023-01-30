/*
Common upload and download related functions
*/

#include <stdint.h>
#include <ftw.h>
#include <unistd.h>
#include <errno.h>

#include <crypt4gh.h>

#include <sodium.h>

#include "include/upcommon.h"
#include "include/upinit.h"
#include "include/uptypes.h"


/*
Key init function, copied over from libcrypt4gh
*/
uint8_t* crypt4gh_session_key_new(void){
    if (sodium_init() == -1) {
        return NULL;
    }
    uint8_t* key = (uint8_t*)sodium_malloc(CRYPT4GH_SESSION_KEY_SIZE * sizeof(uint8_t));

    if(key == NULL || errno == ENOMEM){
        return NULL;
    }

    /* Fill in with random data */
    randombytes_buf(key, CRYPT4GH_SESSION_KEY_SIZE);

    /* Mark it read-only */
    sodium_mprotect_readonly(key);
    return key;
}

/*
wrap filesystem item remove
*/
int nftwremove(
    const char *path,
    const struct stat *st,
    int flag,
    struct FTW *ftws)
{
    if (flag == FTW_F) {
        return unlink(path);
    }
    return 0;
}

/*
Wipe the keys stored in FS
*/
int rmrf() {
    int ret;
    ret = nftw(
        "/keys",
        &nftwremove,
        5, // use at most 5 file descriptors
        0
    );
    ret = nftw(
        "/data",
        &nftwremove,
        5, // use at most 5 file descriptors
        0
    );
    return ret;
}

/*
Allocate chunk.
*/
CHUNK* allocate_chunk() {
    CHUNK* ret;
    ret = malloc(sizeof(CHUNK*));
    ret->chunk = NULL;
    ret->len = 0;
    return ret;
}


/*
Wrap chunk length from pointer
*/
int wrap_chunk_len(CHUNK* chunk) {
    return chunk->len;
}


/*
Wrap chunk content ptr get
*/
uint8_t* wrap_chunk_content(CHUNK* chunk) {
    return chunk->chunk;
}


/*
Free chunk contents.
*/
void free_chunk(CHUNK* chunk) {
    if (chunk->chunk) {
        free(chunk->chunk);
    }
    free(chunk);
    return;
}

/*
Release session resources.
*/
void clean_session(ENCRYPT_SESSION *sess) {
    rmrf();
    close_session(sess);
    return;
}
