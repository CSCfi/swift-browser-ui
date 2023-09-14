/*
Download service worker handlers.
*/


#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#include <crypt4gh/header.h>
#include <crypt4gh/segment.h>
#include <crypt4gh.h>

#include <sodium.h>

#include "include/uptypes.h"
#include "include/upinit.h"
#include "include/upcommon.h"

#include "include/streamingdownload.h"


/*
Open crypt4gh header for file decryption.
*/
uint8_t *get_session_key_from_header(const KEYPAIR *kp, const char *header) {
    uint8_t *sessionkey;

    int ret = 0;
    int fd = open(header, O_RDONLY);

    uint8_t* keys = NULL;
    unsigned int nkeys = 0;
    uint64_t* edit_list = NULL;
    unsigned int edit_list_len = 0;

    ret = crypt4gh_header_parse(
        fd,
        kp->private,
        kp->public,
        &keys,
        &nkeys,
        &edit_list,
        &edit_list_len
    );

    if (edit_list != NULL && edit_list_len > 0) {
        sodium_free(edit_list);
    }

    if (keys != NULL && nkeys > 0) {
        return keys;
    }
    else {
        return NULL;
    }
}


/*
Decrypt a 64KiB + 22 chunk of data.
*/
CHUNK *decrypt_chunk(
    const uint8_t *session_key,
    uint8_t *segment,
    size_t len_segment
) {
    CHUNK *ret = allocate_chunk();
    ret->chunk = malloc(65535 * sizeof(uint8_t));
    int retc = crypt4gh_segment_decrypt(
        session_key,
        segment,
        len_segment,
        ret->chunk,
        &(ret->len)
    );

    return ret;
}
