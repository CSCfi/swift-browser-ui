/*
Download service worker handlers.
*/


#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#include <b64/cencode.h>

#include <crypt4gh/header.h>
#include <crypt4gh/segment.h>
#include <crypt4gh.h>

#include <sodium.h>

#include "include/uptypes.h"
#include "include/upinit.h"
#include "include/upcommon.h"

#include "include/streamingdownload.h"


/*
Open a download session
*/
struct ENCRYPT_SESSION *open_decrypt_session() {
    struct ENCRYPT_SESSION *ret = open_session_enc();

    // Create temporary keys for the session
    randombytes_stir();
    crypto_kx_keypair(
        ret->seckey,
        ret->pubkey
    );

    return ret;
}


/*
Dump crypt4gh public key
*/
char *get_session_public_key(struct ENCRYPT_SESSION *sess) {
    // b64 length = 4 * (32 / 3) rounded to 4 + 1 for `\0`
    char* output = malloc(45 * sizeof(char));
    char* c = output;
    int cnt = 0;

    base64_encodestate s;
    base64_init_encodestate(&s);
    cnt = base64_encode_block(sess->pubkey, 32, c, &s);
    c += cnt;
    cnt = base64_encode_blockend(c, &s);
    c += cnt;
    *c = 0;

    return output;
}


/*
Open crypt4gh header opening for access in JS side.
*/
void open_crypt4gh_header(struct ENCRYPT_SESSION *sess) {
    int ret = 0;
    int fd = open("header", O_RDONLY);

    uint8_t** keys;
    unsigned int nkeys = 0;
    uint64_t** edit_list;
    unsigned int edit_list_len = 0;

    crypt4gh_header_parse(
        fd,
        sess->seckey,
        sess->pubkey,
        keys,
        &nkeys,
        edit_list,
        &edit_list_len
    );

    close(fd);
    return;
}


/*
Decrypt a 64KiB + 22 chunk of data.
*/
struct CHUNK* decrypt_chunk(
    struct ENCRYPT_SESSION *sess,
    uint8_t* segment,
    size_t len_segment
) {
    struct CHUNK* ret = allocate_chunk();
    ret->chunk = malloc(65535 * sizeof(uint8_t));
    crypt4gh_segment_decrypt(
        sess->sessionkey,
        segment,
        len_segment,
        ret->chunk,
        &(ret->len)
    );
    return ret;
}
