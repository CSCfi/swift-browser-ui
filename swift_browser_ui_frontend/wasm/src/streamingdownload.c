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
        ret->pubkey,
        ret->seckey
    );

    return ret;
}


/*
Dump crypt4gh public key
*/
char *get_session_public_key(struct ENCRYPT_SESSION *sess) {
    char *ret = malloc(33 * sizeof(char));
    memset(ret, '\0', 33);
    memcpy(ret, sess->pubkey, 32);
    return ret;
}


/*
Dump crypt4gh private key
*/
char *get_session_private_key(struct ENCRYPT_SESSION *sess) {
    char *ret = malloc(33 * sizeof(char));
    memset(ret, '\0', 33);
    memcpy(ret, sess->seckey, 32);
    return ret;
}


/*
Dump crypt4gh session key
*/
char *get_session_key(struct ENCRYPT_SESSION *sess) {
    char *ret = malloc(33 * sizeof(char));
    memset(ret, '\0', 33);
    memcpy(ret, sess->sessionkey, 32);
    return ret;
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

    ret = crypt4gh_header_parse(
        fd,
        sess->seckey,
        sess->pubkey,
        keys,
        &nkeys,
        edit_list,
        &edit_list_len
    );

    printf("Got %d valid keys.\n", nkeys);

    sess->sessionkey = *keys;

    printf("Header parse return condition: %d\n", ret);

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
    int retc = crypt4gh_segment_decrypt(
        sess->sessionkey,
        segment,
        len_segment,
        ret->chunk,
        &(ret->len)
    );
    printf("Segment decryption return condition %d\n", retc);
    return ret;
}
