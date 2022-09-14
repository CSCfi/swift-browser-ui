/*
Upload service worker handlers
*/

#define _XOPEN_SOURCE 500


#include <stdint.h>
#include <errno.h>
#include <ftw.h>
#include <unistd.h>

#include <crypt4gh/header.h>
#include <crypt4gh/segment.h>
#include <crypt4gh.h>

#include "include/uptypes.h"
#include "include/upinit.h"

#include "include/streamingupload.h"


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
Key init function, copied over from libcrypt4gh
*/
static uint8_t* crypt4gh_session_key_new(void){
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
Open an ephemeral key upload session
*/
struct ENCRYPT_SESSION *open_session_eph() {
    struct ENCRYPT_SESSION *ret = open_session_enc();
    read_in_recv_keys(ret);
    ret->sessionkey = crypt4gh_session_key_new();
    return ret;
}


/* 
Open an upload session
*/
struct ENCRYPT_SESSION *open_session(
    const char *passphrase // optional
) {
    struct ENCRYPT_SESSION *ret = open_session_enc();
    read_in_keys(
        passphrase,
        ret);
    ret->sessionkey = crypt4gh_session_key_new();
    return ret;
}


/*
Allocate chunk.
*/
struct CHUNK* allocate_chunk() {
    struct CHUNK* ret;
    ret = malloc(sizeof(struct CHUNK*));
    ret->chunk = NULL;
    ret->len = 0;
    return ret;
}


/*
Wrap crypt4gh header creation for access in JS side.
*/
struct CHUNK* wrap_crypt4gh_header(struct ENCRYPT_SESSION *sess) {
    struct CHUNK* ret = allocate_chunk();
    crypt4gh_header_build(
        sess->sessionkey,
        sess->seckey,
        sess->recv_keys,
        sess->recv_key_amount,
        &(ret->chunk),
        &(ret->len));
    return ret;
}


/*
Wrap chunk length from pointer
*/
int wrap_chunk_len(struct CHUNK* chunk) {
    return chunk->len;
}


/*
Wrap chunk content ptr get
*/
uint8_t* wrap_chunk_content(struct CHUNK* chunk) {
    return chunk->chunk;
}


/*
Free chunk contents.
*/
void free_chunk(struct CHUNK* chunk) {
    if (chunk->chunk) {
        free(chunk->chunk);
    }
    free(chunk);
    return;
}


/*
Encrypt a 64KiB chunk of data.
*/
struct CHUNK* encrypt_chunk(
    struct ENCRYPT_SESSION *sess,
    uint8_t* segment,
    size_t len_segment
) {
    struct CHUNK* ret = allocate_chunk();
    ret->chunk = malloc(CRYPT4GH_CIPHERSEGMENT_SIZE * sizeof(uint8_t));
    crypt4gh_segment_encrypt(
        sess->sessionkey,
        segment,
        len_segment,
        ret->chunk,
        &(ret->len)
    );
    return ret;
}


/*
Release session resources.
*/
void clean_session(struct ENCRYPT_SESSION *sess) {
    rmrf();
    close_session(sess);
    return;
}
